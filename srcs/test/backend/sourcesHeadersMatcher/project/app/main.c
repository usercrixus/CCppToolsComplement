#include <stdio.h>
#include "../config/feature.h"
#include "../services/io/log.h"
#include "../services/math/adjust.h"
#include "../services/math/compute.h"

int main(void)
{
    int total = compute_total(20, 14);

#ifdef MAIN_LOG_BEFORE_ADJUST
    log_result(total);
#endif

    total = adjust_total(total);
    total = adjust_twice(total);

#ifdef MAIN_APPLY_IDENTITY_TWICE
    total = log_identity(total);
#endif

    total = log_identity(total);

    log_result(total);
    printf("%s\n", feature_name());
    return 0;
}
