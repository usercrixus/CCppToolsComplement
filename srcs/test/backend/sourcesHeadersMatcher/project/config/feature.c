#define FEATURE_NAME "sourcesHeadersMatcher fixture"

typedef struct runtime_flag {
    const char *label;
    int is_active;
} runtime_flag_t;

struct feature_toggle;
const char *feature_name(void);

struct feature_toggle {
    const char *name;
    int enabled;
};

const char *feature_name(void)
{
    runtime_flag_t flag = {"fixture", 1};

    (void)flag;
    return FEATURE_NAME;
}
