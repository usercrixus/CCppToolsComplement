#include <stdio.h>

int compute_total(int base, int extra);
void log_result(int value);
const char *feature_name(void);

int main(void)
{
    int total = compute_total(20, 22);

    log_result(total);
    printf("%s\n", feature_name());
    return 0;
}
