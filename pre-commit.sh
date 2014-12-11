# Stash changes to ensure code outside of commit is not tested
git stash -q --keep-index

python setup.py test
RESULT=$?

# Unstash
git stash pop -q
[ $RESULT -ne 0 ] && echo "Testing failed, aborting commit. (Use git commit --no-verify to skip tests)"
[ $RESULT -ne 0 ] && exit 1
exit 0

