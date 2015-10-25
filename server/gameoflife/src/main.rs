
//use serialize::base64::{self, ToBase64};



extern crate rustc_serialize;
//use rustc_serialize::base64;
use rustc_serialize::base64::FromBase64;

use std::env;


// TODO: take these as command line args
const WIDTH : usize = 57;
const HEIGHT : usize = 44;

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


fn main() {

    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("Please provide initial board state");
        std::process::exit(0);
    }

    let initial_board = &args[1];    // Can't "take" args[1], it is owned

    let bin_board = initial_board.from_base64().unwrap();
    //assert_eq!(initial_board_res.is_ok(), true);
    //let bin_board = initial_board_res.ok();

    let mut board = [[false; HEIGHT]; WIDTH];

    println!("Initial board: {}", initial_board);
    println!("Bin boad: {:?} {}", bin_board, bin_board.len());

    for x in 0..WIDTH {
        for y in 0..HEIGHT {
            let idx = (x*HEIGHT) + y;
            let px = bin_board[(idx / 8)] & (1 << (idx % 8));
            board[x][y] = (px != 0);
        }
    }
    print_board(&board);
}
