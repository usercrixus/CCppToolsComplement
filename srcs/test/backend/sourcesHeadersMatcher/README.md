# sourcesHeadersMatcher fixture

This folder contains a small badly-organized C project to exercise
`srcs/vscodeIntegration/backend/sourcesHeadersMatcher/main.py`.

Initial state:
- declarations grouped in an unrelated source file
- implementations spread across nested folders
- local `.h` files already present in `config/`, `services/io/` and `services/math/`
- one extra `adjust.c` / `adjust.h` pair to exercise another generated header/source mapping
- one macro, one forward-declared struct and one typedef living in a `.c` file

Suggested command from the repository root:

```bash
python3 srcs/vscodeIntegration/backend/sourcesHeadersMatcher/main.py \
  srcs/test/backend/sourcesHeadersMatcher/project
```

```bash
git restore --source=HEAD -- srcs/test/backend/sourcesHeadersMatcher/project
```

Useful files:
- `project/catalog/declarations.c`: misplaced declarations
- `project/config/feature.h`: existing local header consumed by `app/main.c`
- `project/services/math/compute.c`: function implementation
- `project/services/math/adjust.c`: additional function implementation
- `project/services/math/adjust.h`: declaration for the extra math function
- `project/services/io/log.c`: function implementation
- `project/config/feature.c`: macro, struct, typedef and function implementation
- `project/app/main.c`: consumer using the declarations
- `project/conditional/variant.h`: nested `#ifdef` / `#ifndef` declarations for conditional path expansion
- `project/conditional/variant.c`: nested `#ifdef` / `#ifndef` implementations for conditional path expansion
