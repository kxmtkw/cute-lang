
#ifndef CT_ERROR_H
#define CT_ERROR_H

#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>

#include "common/config.h"

typedef enum {
	CT_ERROR_LEVEL_ENGINE = 0x00,
	CT_ERROR_LEVEL_LIB = 0x01,
	CT_ERROR_LEVEL_USER = 0x02,
} CtErrorLevel;


typedef struct {
	bool          raised;
	CtErrorLevel  level;
	char*         domain;
	char*         subdomain;
	char*         topic;
	char          details[256];
} CtError;


#define CT_ERROR(ERROR, LEVEL, DOMAIN, SUBDOMAIN, TOPIC, DETAILS, ...) \
ERROR.domain = DOMAIN; ERROR.subdomain = SUBDOMAIN; ERROR.topic = TOPIC; \
ct_utils_format(ERROR.details, sizeof(ERROR.details), DETAILS, __VA_ARGS__); \
ERROR.raised = true; \
ERROR.level = LEVEL;

#define CT_ERROR_ENGINE(ERROR, SUBDOMAIN, TOPIC, DETAILS, ...) \
CT_ERROR(ERROR, CT_ERROR_LEVEL_ENGINE, CT_CONF_INTERNAL_ERROR_DOMAIN, SUBDOMAIN, TOPIC, DETAILS, __VA_ARGS__)

#define CT_ERROR_LIB(ERROR, SUBDOMAIN, TOPIC, DETAILS, ...) \
CT_ERROR(ERROR, CT_ERROR_LEVEL_LIB, CT_CONF_INTERNAL_ERROR_DOMAIN, SUBDOMAIN, TOPIC, DETAILS, __VA_ARGS__)

#define CT_ERROR_USER(ERROR, DOMAIN, SUBDOMAIN, TOPIC, DETAILS, ...) \
CT_ERROR(ERROR, CT_ERROR_LEVEL_USER, DOMAIN, SUBDOMAIN, TOPIC, __VA_ARGS__)

#define CT_COLOR_RED "\033[31m"
#define CT_COLOR_RESET "\033[0m"

static inline void
ct_error_print(CtError* err) {
	printf(CT_COLOR_RED"%s/%s/%s"CT_COLOR_RESET" %s\n", err->domain, err->subdomain, err->topic, err->details);
}


#endif // CT_ERROR_H