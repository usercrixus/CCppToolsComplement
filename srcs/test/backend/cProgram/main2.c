#include <stdio.h>
#include "subfolder/header.h"
#include "subfolder/two.h"
#include "one.h"

int main()
{
    printf(DEFINE_TEST);
    printf("\n");
    print_one();
    printf("\n");
    print_two();
    printf("\n");
    return 0;
}
