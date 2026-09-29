#include <stdarg.h>

#include "utils/utils.h"

int ct_utils_format(char* buffer, size_t size, const char* format, ...) {

    if (!buffer || size == 0 || !format) return 0;

    va_list args;
    va_start(args, format);
    int written = vsnprintf(buffer, size, format, args);
    va_end(args);

    return written;
}

