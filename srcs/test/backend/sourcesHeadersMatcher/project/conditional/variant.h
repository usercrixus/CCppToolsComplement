#pragma once

const char *variant_name(void);

#ifdef VARIANT_FAST
const char *variant_fast_label(void);
#ifndef VARIANT_SAFE
const char *variant_fast_unsafe_label(void);
#ifdef VARIANT_TRACE
const char *variant_fast_unsafe_trace_label(void);
#endif
#endif
#else
const char *variant_default_label(void);
#endif
