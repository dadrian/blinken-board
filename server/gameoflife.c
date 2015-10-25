


#include <stdio.h>
#include "libgameoflife.h"

int
main()
{
    uint32_t generations;
    uint32_t min_gens = 10000;
    unsigned char *board = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD+emin+COoMMiVILpAS2broitX6Ycuuu7kS+ki6DmfsCD+qqqq+gOA3OE0AJAM3JNx4wRHpi8OnIlIUsCgl0FYFQmCI1PfWkJ2QOSnJp5Vi8G54QOrhm06gJIVjYChlgdG/xiOKkt8KGGgDCDAGfDB3312orLCo7c68KsW0EMBIGAd1hOqRqANqOMQagLxNqiWcXk34fGb0eExnsmJET3DQmLEdxnyRa96DIBGuB0AHMKpT1++ASBypzUe/oy0qOsjyHpSKRq6EHeiP6KrHG4tMroc5rBjIghWPGMV/rhiO7gBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";

    printf("runs for %d gens\n", how_many_generations(board, min_gens));
}
