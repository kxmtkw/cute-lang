#ifndef CUTE_CONFIG_H
#define CUTE_CONFIG_H

/* 

Cute Engine configuration options. Can customize these to change the behavior of the engine

*/

// Maximum recursive calls allowed.
#define CT_CONF_CALLSTACK_SIZE 1000

// Whether to fail on the 0x00 instruction or just to ignore it.
#define CT_CONF_FAIL_ON_NULL

// Base Domain for all errors occurring inside the engine.
#define CT_CONF_INTERNAL_ERROR_DOMAIN "Cute"

/*
Whether to run in debug mode or not.
For now, debug mode offers:
- Rich logs for each and every subsystem of the engine.
*/
// #define CT_CONF_DEBUG


#ifdef CT_CONF_DEBUG

/*
The log filter to use.
For example, if one is working on the object manager, and the rest of the logs are unneeded, the filter can be set to (DOMAIN == "objects")
*/
#define CT_CONF_LOG_FILTER(DOMAIN) true

#define CT_LOG(DOMAIN, ...) \
    do { \
		if (CT_CONF_LOG_FILTER(DOMAIN)) {\
			printf("[LOG] (%s) ", DOMAIN); \
			printf(__VA_ARGS__); \
		} \
    } while (0)

#else

#define CT_LOG(DOMAIN, ...) do {} while (0)

#endif // CT_CONF_DEBUG


// Constants, These should not be changed at all because changing them will literally have no effect on the code.
// Just here for the sake of it.
#define CT_CONF_FIXED_SLOT_COUNT 256
#define CT_CONF_FIXED_CON_BUCKET_SIZE 1024



#endif // CUTE_CONFIG_H