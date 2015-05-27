#include "xdo.h"
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <event2/event.h>
#include <event2/bufferevent.h>
#include <event2/listener.h>
#include <string.h>

#define LISTEN_PORT 8888

struct key {
    int is_down;
    uint64_t mask;  // lucky for us, it's only 8 bytes
    int reversed;   // pressed if the bit is cleared, instead of set
    char *send;     // key press to send when pressed
};

struct state_st {

    xdo_t *xdo;
    Window window;
    struct key *keys;
    int num_keys;

    uint64_t frames_read;
};

void press_keys(struct state_st *state, uint64_t events)
{
    int i;
    static uint64_t last_events;
    if (events != last_events) {
        last_events = events;

        //printf("%016lx\n", events);
        //printf("%016lx\n", events & state->keys[0].mask);
    }
    for (i=0; i<state->num_keys; i++) {
        if (events & state->keys[i].mask) {
            if (!state->keys[i].reversed && !state->keys[i].is_down) {
                // press this key down
                xdo_send_keysequence_window_down(state->xdo, state->window, state->keys[i].send, 0);
                state->keys[i].is_down = 1;
                printf("down: %s\n", state->keys[i].send);

            } else if (state->keys[i].reversed && state->keys[i].is_down) {
                // release this key up
                xdo_send_keysequence_window_up(state->xdo, state->window, state->keys[i].send, 0);
                state->keys[i].is_down = 0;
                printf("up: %s\n", state->keys[i].send);
            }
        } else {
            if (!state->keys[i].reversed && state->keys[i].is_down) {
                // release this key up
                xdo_send_keysequence_window_up(state->xdo, state->window, state->keys[i].send, 0);
                state->keys[i].is_down = 0;
                printf("up: %s\n", state->keys[i].send);

            } else if (state->keys[i].reversed && !state->keys[i].is_down) {
                // press this key down
                xdo_send_keysequence_window_down(state->xdo, state->window, state->keys[i].send, 0);
                state->keys[i].is_down = 1;
                printf("down: %s\n", state->keys[i].send);
            }
        }
    }
}


void read_cb(struct bufferevent *bev, void *arg)
{
    struct state_st *state = arg;
    uint64_t events;
    struct evbuffer *input = bufferevent_get_input(bev);
    int had_input = 0;

    // TODO: use math and evbuffer_drain to save on copying
    while (evbuffer_get_length(input) >= sizeof(events)) {
        evbuffer_remove(input, &events, sizeof(events));
        press_keys(state, events);

        state->frames_read++;
        had_input = 1;
    }
}


void status_cb(evutil_socket_t fd, short what, void *arg)
{
    struct state_st *state = arg;
    printf("%lu frames/sec\n", state->frames_read);

    state->frames_read = 0;
}


void accept_conn_cb(struct evconnlistener *listener,
    evutil_socket_t fd, struct sockaddr *address, int socklen,
    void *arg)
{
        struct state_st *state = arg;
        struct event_base *base = evconnlistener_get_base(listener);
        struct bufferevent *bev = bufferevent_socket_new(
                base, fd, BEV_OPT_CLOSE_ON_FREE);

        bufferevent_setcb(bev, read_cb, NULL, NULL, state);

        bufferevent_enable(bev, EV_READ|EV_WRITE);
}


void setup_keys(struct state_st *state)
{
    state->keys = malloc(sizeof(struct key)*8);

    // A
    //state->keys[0].mask = 0x0000000000200000;
    state->keys[0].mask = 0x0000200000000000;
    state->keys[0].send = "x";

    // B
    //state->keys[1].mask = 0x0000000000400000;
    state->keys[1].mask = 0x0000400000000000;
    state->keys[1].send = "z";

    // start
    //state->keys[2].mask = 0x0000000000002000;
    state->keys[2].mask = 0x0020000000000000;
    state->keys[2].send = "Return";

    // select
    //state->keys[3].mask = 0x0000000000001000;
    state->keys[3].mask = 0x0010000000000000;
    state->keys[3].send = "Ctrl";

    // right
    //state->keys[4].mask = 0x0000008000000000;
    state->keys[4].mask = 0x0000000080000000;
    state->keys[4].send = "Right";

    // down
    //state->keys[5].mask = 0x0000000080000000;
    state->keys[5].mask = 0x0000008000000000;
    state->keys[5].send = "Down";

    // left
    //state->keys[6].mask = 0x0000000100000000;
    state->keys[6].mask = 0x0000000001000000;
    state->keys[6].reversed = 1;
    state->keys[6].send = "Left";

    // up
    //state->keys[7].mask = 0x0000000001000000;
    state->keys[7].mask = 0x0000000100000000;
    state->keys[7].reversed = 1;
    state->keys[7].send = "Up";

    state->num_keys = 8;

}



int main(int argc, char *argv[])
{

    struct event_base *base;
    int port = LISTEN_PORT;
    struct sockaddr_in sin;
    struct state_st state;
    struct evconnlistener *listener;
    struct event *ev;

    memset(&sin, 0, sizeof(sin));
    memset(&state, 0, sizeof(state));

    setup_keys(&state);
    state.xdo = xdo_new(":0");
    state.window = CURRENTWINDOW;

    base = event_base_new();

    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);

    listener = evconnlistener_new_bind(base, accept_conn_cb, &state,
            LEV_OPT_CLOSE_ON_FREE|LEV_OPT_REUSEABLE, -1,
            (struct sockaddr*)&sin, sizeof(sin));


    struct timeval one_sec = {1, 0};
    ev = event_new(base, 0, EV_PERSIST, status_cb, &state);
    event_add(ev, &one_sec);

    event_base_dispatch(base);

    return 0;
}
