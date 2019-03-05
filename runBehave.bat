setlocal

path=%path%;env\scripts

if '%1' == '' behave
if not '%1' == '' behave --include %1
