#![crate_type = "dylib"]


extern crate rustc_serialize;
extern crate libc;

use rustc_serialize::base64::FromBase64;
use std::ffi::CString;
use std::ffi::CStr;
use std::str;
use std::env;


// TODO: take these as command line args
const WIDTH : usize = 57;
const HEIGHT : usize = 44;

#[allow(dead_code)]
fn print_board(board :&[[bool; HEIGHT]]) {
    for y in 0..HEIGHT {
        for x in 0..WIDTH {
            if board[x][y] {
                print!("X");
            } else {
                print!(" ");
            }
        }
        print!("\n");
    }
}

fn wrap_add(x :usize, i :i32, bound: usize) -> usize {
    let check_x :usize = match i {
        -1 => x.checked_sub(1).unwrap_or(bound.checked_sub(1).unwrap()),
        0 => x,
        1 => if x + 1 == bound { 0 } else { x + 1 },
        _ => 0, // Error???
    };
    check_x
}

fn count_live_neighbors(board :&[[bool; HEIGHT]], x :usize, y :usize) -> usize {
    let mut live :usize = 0;

    for i in -1..2 {
        let check_x = wrap_add(x, i, WIDTH);
        for j in -1..2 {
            let check_y = wrap_add(y, j, HEIGHT);
            if !(x==check_x && y==check_y) && board[check_x][check_y] {
                live += 1;
            }
        }
    }
    live
}

fn copy_board(source :&[[bool; HEIGHT]], dest :&mut [[bool; HEIGHT]]) {
    for x in 0..WIDTH {
        for y in 0..HEIGHT {
            dest[x][y] = source[x][y];
        }
    }
}

// Just overwrite the referenced board at the end
fn do_generation(board :&mut [[bool; HEIGHT]]) {
    let mut new_board = [[false; HEIGHT]; WIDTH];


    for x in 0..WIDTH {
        for y in 0..HEIGHT {
            let live = count_live_neighbors(board, x, y);
            if board[x][y] && (live < 2 || live > 3) {
                // Die
                new_board[x][y] = false;
            } else if !board[x][y] && live == 3 {
                // Born
                new_board[x][y] = true;
            } else {
                // Carry on
                new_board[x][y] = board[x][y];
            }
        }
    }

    // Copy board (memcpy? something better and safe?)
    copy_board(&new_board, board);
}

fn board_equal(b1 :&[[bool; HEIGHT]], b2 :&[[bool; HEIGHT]]) -> bool {
    for x in 0..WIDTH {
        for y in 0..HEIGHT {
            if b1[x][y] != b2[x][y] {
                return false;
            }
        }
    }
    return true;
}


#[no_mangle]
pub extern fn how_many_generations(initial_board_cstr :*const libc::c_char, max_generations: u32) -> u32 {

    let initial_board :&str;
    unsafe {
        initial_board = str::from_utf8(CStr::from_ptr(initial_board_cstr).to_bytes()).unwrap();
        //to_string_lossy().into_owned();
    }
    let bin_board = initial_board.from_base64().unwrap();
    //assert_eq!(initial_board_res.is_ok(), true);
    //let bin_board = initial_board_res.ok();

    let mut board = [[false; HEIGHT]; WIDTH];

    //println!("Initial board: {}", initial_board);
    //println!("Bin boad: {:?} {}", bin_board, bin_board.len());

    for x in 0..WIDTH {
        for y in 0..HEIGHT {
            let idx = (x*HEIGHT) + y;
            let px = bin_board[(idx / 8)] & (1 << (idx % 8));
            board[x][y] = px != 0;
        }
    }
    //print_board(&board);

    let mut t1 = [[false; HEIGHT]; WIDTH];
    let mut two_ago = [[false; HEIGHT]; WIDTH];

    for generation in 0..max_generations {
        do_generation(&mut board);

        // Compare this to two iterations ago
        if board_equal(&board, &two_ago) {
            /*
            print_board(&board);
            println!("----");
            print_board(&t1);
            println!("----");
            print_board(&two_ago);
            println!("Stuck in loop after {} generations", generation);
            */
            return generation;
        }

        copy_board(&t1, &mut two_ago);
        copy_board(&board, &mut t1);

    }

    max_generations
}

fn main() {

    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!("Please provide number of generations and initial board state");
        std::process::exit(0);
    }

    let max_generations = args[1].parse::<u32>().unwrap();
    let initial_board = &args[2];    // Can't "take" args[1], it is owned

    let initial_board_cstr = CString::new(initial_board.to_string()).unwrap();

    let generations = how_many_generations(initial_board_cstr.as_ptr(), max_generations);

    println!("{}", generations);
}
