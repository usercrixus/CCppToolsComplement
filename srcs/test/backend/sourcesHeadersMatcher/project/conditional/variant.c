#include "variant.h"

const char *variant_name(void)
{
    return "variant";
}

#ifdef VARIANT_FAST
const char *variant_fast_label(void)
{
    return "fast";
}
#ifndef VARIANT_SAFE
const char *variant_fast_unsafe_label(void)
{
    return "fast-unsafe";
}
#ifdef VARIANT_TRACE
const char *variant_fast_unsafe_trace_label(void)
{
    return "fast-unsafe-trace";
}
#endif
#endif
#else
const char *variant_default_label(void)
{
    return "default";
}
#endif
