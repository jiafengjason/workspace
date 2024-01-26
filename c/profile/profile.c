//gcc -o profile profile.c
#include <stdio.h>
#include <stdlib.h>
#include <libgen.h>
#include <string.h>
#include <glob.h>
#include <pwd.h>
#include <unistd.h>

#define MAX_READ 8192

typedef struct profile_entry_t {
    struct profile_entry_t *next;
    char *data;
} ProfileEntry;

ProfileEntry *whitelist;
ProfileEntry *nowhitelist;
ProfileEntry *blacklist;
ProfileEntry *mergewhitelist;
ProfileEntry *mergelist;

/*
void globbing(OPERATION op, const char *pattern, const char *noblacklist[], size_t noblacklist_len) {

    glob_t globbuf;

    int globerr = glob(pattern, GLOB_NOCHECK | GLOB_NOSORT | GLOB_PERIOD, NULL, &globbuf);
    if (globerr) {
        syslog(LOG_INFO, "Error: failed to glob pattern %s\n", pattern);
    	exit(1);
    }

	size_t i, j;
	for (i = 0; i < globbuf.gl_pathc; i++) {
		char *path = globbuf.gl_pathv[i];
		assert(path);
		// /home/me/.* can glob to /home/me/.. which would blacklist /home/
		const char *base = gnu_basename(path);
		if (strcmp(base, ".") == 0 || strcmp(base, "..") == 0)
			continue;
		// noblacklist is expected to be short in normal cases, so stupid and correct brute force is okay
		bool okay_to_blacklist = true;
		if (op == BLACKLIST_FILE || op == BLACKLIST_NOLOG) {
			for (j = 0; j < noblacklist_len; j++) {
				int result = fnmatch(noblacklist[j], path, FNM_PATHNAME);
				if (result == FNM_NOMATCH)
					continue;
				else if (result == 0) {
					okay_to_blacklist = false;
#ifdef TEST_NO_BLACKLIST_MATCHING
					if (j < nbcheck_size)	// noblacklist checking
						nbcheck[j] = 1;
#endif
					break;
				}
				else {
					fprintf(stderr, "Error: failed to compare path %s with pattern %s\n", path, noblacklist[j]);
					exit(1);
				}
			}
		}

		if (okay_to_blacklist)
			disable_file(op, path);
		else if (arg_debug)
			printf("Not blacklist %s\n", path);
	}
	globfree(&globbuf);
}

static int hide_lowlayer_path(char *path, char *whitelist[], char *blacklist[])
{
    int i = 0;
    int len = 0;
    char hide_path[1024] = {0};
    char special_paths[][32] = {
        "Desktop",
        "Documents",
        "Downloads",
        "Music",
        "Pictures",
        "Public",
        "Templates",
        "Videos"
    };

    if (0 == strncmp(path, home, strlen(home))) {
        if (0 == strncmp(name, ".", strlen("."))) {
            return 0;
        }
        for (i = 0; i<sizeof(special_paths)/32; i++) {
            if (0 == strncmp(name, special_paths[i], strlen(special_paths[i]))) {
                return 0;
            }
        }
        syslog(LOG_INFO, "hide_lowlayer_path path=%s name=%s\n", path, name);
        return 1;
    }

    for (i = 0; i<sizeof(special_paths)/32; i++) {
        snprintf(hide_path, sizeof(hide_path), "%s/%s", home, special_paths[i]);
        if (0 == strncmp(path, hide_path, strlen(hide_path))) {
            syslog(LOG_INFO, "hide_lowlayer_path path=%s name=%s\n", path, name);
            return 1;
        }
        memset(hide_path, 0, sizeof(hide_path));
    }

    return 0;
}
*/

char *line_remove_spaces(const char *buf) {
    size_t len = strlen(buf);
    if (len == 0)
        return NULL;

    // allocate memory for the new string
    char *rv = malloc(len + 1);
    if (rv == NULL)
        return NULL;

    // remove space at start of line
    const char *ptr1 = buf;
    while (*ptr1 == ' ' || *ptr1 == '\t')
        ptr1++;

    // copy data and remove additional spaces
    char *ptr2 = rv;
    int state = 0;
    while (*ptr1 != '\0') {
        if (*ptr1 == '\n' || *ptr1 == '\r')
            break;

        if (state == 0) {
            if (*ptr1 != ' ' && *ptr1 != '\t')
                *ptr2++ = *ptr1++;
            else {
                *ptr2++ = ' ';
                ptr1++;
                state = 1;
            }
        }
        else {  // state == 1
            while (*ptr1 == ' ' || *ptr1 == '\t')
                ptr1++;
            state = 0;
        }
    }

    if (ptr2 > rv && *(ptr2 - 1) == ' ')
        --ptr2;
    *ptr2 = '\0';

    return rv;
}

const char *gnu_basename(const char *path) {
    const char *last_slash = strrchr(path, '/');
    if (!last_slash)
        return path;
    return last_slash+1;
}

void profile_add_list(char *str, ProfileEntry **list) {
    ProfileEntry *prf = malloc(sizeof(ProfileEntry));
    if (!prf) {
        printf("prf is NULL\n");
        return;
    }
    memset(prf, 0, sizeof(ProfileEntry));
    prf->next = NULL;
    prf->data = str;

    if (*list == NULL) {
        *list = prf;
        return;
    }
    ProfileEntry *ptr = *list;
    while (ptr->next != NULL)
        ptr = ptr->next;
    ptr->next = prf;
}

void profile_add_globlist(char *str, ProfileEntry **list) {
    size_t i;
    glob_t globbuf;
    char *path = NULL;

    int globerr = glob(str, GLOB_NOCHECK | GLOB_NOSORT | GLOB_PERIOD, NULL, &globbuf);
    if (globerr) {
        printf("Error: failed to glob pattern %s\n", str);
        return;
    }

    for (i = 0; i < globbuf.gl_pathc; i++) {
        path = globbuf.gl_pathv[i];
        //printf("path: %s\n", path);

        const char *base = gnu_basename(path);
        if (strcmp(base, ".") == 0 || strcmp(base, "..") == 0)
            continue;

        profile_add_list(strdup(path), list);
    }

    globfree(&globbuf);
}

void profile_mergelist(ProfileEntry **includelist, ProfileEntry **excludelist, ProfileEntry **mergelist) {
    ProfileEntry *includeentry;
    ProfileEntry *excludeentry;
    int mergeflag = 1;

    includeentry = *includelist;
    while (includeentry) {
        mergeflag = 1;
        excludeentry = *excludelist;
        while (excludeentry) {
            if (strcmp(includeentry->data, excludeentry->data) == 0) {
                mergeflag = 0;
                break;
            }

            excludeentry = excludeentry->next;
        }

        if(mergeflag) {
            profile_add_list(includeentry->data, mergelist);
        }
        includeentry = includeentry->next;
    }

}

char *expand_macros(char *path) {
    char *new_name = NULL;

    struct passwd *pw = getpwuid(getuid());
    if (strncmp(path, "$HOME", 5) == 0) {
        printf("Error: $HOME is not allowed in profile files, please replace it with ${HOME}\n");
        exit(1);
    }
    else if (strncmp(path, "${HOME}", 7) == 0) {
        asprintf(&new_name, "%s%s", pw->pw_dir, path + 7);
        return new_name;
    }
    else if (*path == '~') {
        asprintf(&new_name, "%s%s", pw->pw_dir, path + 1);
        return new_name;
    }

    return strdup(path);
}

int main() {
    char buf[MAX_READ + 1];
    int lineno = 0;
    ProfileEntry *entry;
    char *ptr = NULL;
    char *new_name = NULL;

    FILE *fp = fopen("profile.config", "r");
    if (fp == NULL) {
        printf("Error: cannot open profile file %s\n", "profile.config");
        exit(1);
    }

    while (fgets(buf, MAX_READ, fp)) {
        ++lineno;
        
        ptr = line_remove_spaces(buf);
        if (ptr == NULL)
            continue;
        
        if (*ptr == '#' || *ptr == '\0') {
            free(ptr);
            continue;
        }

        if (strncmp(ptr, "whitelist ", 10) == 0) {
            new_name = expand_macros(ptr+10);
            if (new_name) {
                profile_add_globlist(new_name, &whitelist);
            }
        } else if (strncmp(ptr, "nowhitelist ", 12) == 0) {
            new_name = expand_macros(ptr+12);
            if (new_name) {
                profile_add_globlist(new_name, &nowhitelist);
            }
        } else if (strncmp(ptr, "blacklist ", 10) == 0) {
            new_name = expand_macros(ptr+10);
            if (new_name) {
                profile_add_globlist(new_name, &blacklist);
            }
        }
        if (new_name)
            free(new_name);
    }

    profile_mergelist(&whitelist, &nowhitelist, &mergewhitelist);
    profile_mergelist(&blacklist, &mergewhitelist, &mergelist);

    printf("whitelist----------------------\n");
    entry = mergewhitelist;
    while (entry) {
        printf("whitelist %s\n", entry->data);
        entry = entry->next;
    }

    printf("blacklist----------------------\n");
    entry = blacklist;
    while (entry) {
        printf("blacklist %s\n", entry->data);
        entry = entry->next;
    }

    printf("mergelist----------------------\n");
    entry = mergelist;
    while (entry) {
        printf("mergelist %s\n", entry->data);
        entry = entry->next;
    }

    return 0;
}
