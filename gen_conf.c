#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void conf_from_input(FILE *fd, char *key, size_t length);

int main(int argc, char *argv[])
{
	FILE *fd = fopen("autopwn.conf", "w+");
	if (!fd) {
		perror("Can not create config file.\n");
		exit(EXIT_FAILURE);
	}
	conf_from_input(fd, "FILE_NAME", 10);
	conf_from_input(fd, "SERVER_ADDR", 45);
	conf_from_input(fd, "SERVER_CLASS", 10);
	fclose(fd);	
	printf("done.\n");	
	return 0;
}

void conf_from_input(FILE *fd, char *key, size_t length)
{
	char *value  = calloc(sizeof(char), length);
	printf("%s: ", key);
	fgets(value, length, stdin);
	value[strlen(value) - 1] = 0;
	fprintf(fd, "%s: \"%s\"\n", key, value);
	free(value);
}


