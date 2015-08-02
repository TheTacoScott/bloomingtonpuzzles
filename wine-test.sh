#!/bin/bash
echo -n "People Errors: "
cat "$@" | grep -Eio "p[0-9]{1,50}" | uniq -c | grep -vE "^[ \t]*[1-3] p[0-9]{1,50}" | wc -l
echo -n "Wine Errors: "
cat "$@" | grep -Eio "w[0-9]{1,50}" | uniq -c | grep -vE "^[ \t]*1 w[0-9]{1,50}" | wc -l
