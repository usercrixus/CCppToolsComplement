#include <stdio.h>
#include "subfolder/header.h"
#include "subfolder/two.h"
#include "one.h"

int main()
{
    int test_ok = 10;
    printf(DEFINE_TEST);
    printf("\n");
    print_one();
    printf("\n");
    print_two();
    printf("\n");
    return 0;
}
