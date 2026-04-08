#include <stdio.h>
#include "../config/feature.h"
#include "../services/io/log.h"
#include "../services/math/adjust.h"
#include "../services/math/compute.h"

int main(void)
{
    int total = compute_total(20, 14);
    total = adjust_total(total);
    total = adjust_twice(total);
    total = log_identity(total);

    log_result(total);
    printf("%s\n", feature_name());
    return 0;
}
