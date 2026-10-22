"""CI guard: did the change make the build green by weakening the tests?

    python3 guard/test_guard.py <base project> <changed project>

Both arguments are Maven project directories: the target branch and the branch
with the change (for a pull request, two checkouts of the same repository).

Two checks:

1. Static. For every test file that differs from the base: fewer assert calls,
   fewer @Test methods, a new @Disabled, a removed or renamed test, changed
   asserts inside a test method. Each finding is a warning for the reviewer,
   not a reason to block: tests do change.

2. Dynamic, the one that blocks. The changed tests are run against the BASE
   production code. A test that failed on the base code with the base tests
   caught a real difference in behaviour. If, after the change, the same test
   passes on the same base code, the test no longer sees that difference, so
   it was made weaker. The same goes for a test that disappeared.

Exit code 1 means "block the merge", exit code 2 means "the tests did not run
at all" (a build error, not a verdict).
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

TEST_DIR = pathlib.Path("src/test/java")
MAIN_DIR = pathlib.Path("src/main/java")

ASSERT = re.compile(r"\bassert\w*\s*\(")
TEST_METHOD = re.compile(r"@Test\b")
DISABLED = re.compile(r"@Disabled\b")
LITERAL = re.compile(r'"[^"\n]*"|\b\d+(?:\.\d+)?\b')
METHOD = re.compile(r"^\s*(?:public\s+|protected\s+)?void\s+(\w+)\s*\(")


def java_files(root):
    return {p.relative_to(root): p.read_text(encoding="utf-8")
            for p in sorted(root.rglob("*.java"))} if root.exists() else {}


def static_findings(base, changed):
    base_tests = java_files(base / TEST_DIR)
    new_tests = java_files(changed / TEST_DIR)
    findings = []
    for path in sorted(set(base_tests) | set(new_tests)):
        old, new = base_tests.get(path, ""), new_tests.get(path, "")
        if old == new:
            continue
        if not new:
            findings.append(f"{path}: test file removed")
            continue
        if not old:
            continue
        for name, pattern in (("assert calls", ASSERT), ("@Test methods", TEST_METHOD)):
            before, after = len(pattern.findall(old)), len(pattern.findall(new))
            if after < before:
                findings.append(f"{path}: {name} {before} -> {after}")
        if len(DISABLED.findall(new)) > len(DISABLED.findall(old)):
            findings.append(f"{path}: new @Disabled")
        old_methods, new_methods = methods(old), methods(new)
        for method in sorted(old_methods):
            if method not in new_methods:
                findings.append(f"{path}: test {method} removed or renamed")
            elif old_methods[method] != new_methods[method]:
                findings.append(f"{path}: asserts changed in {method}")
    old_pom, new_pom = base / "pom.xml", changed / "pom.xml"
    if old_pom.exists() and new_pom.exists() and old_pom.read_bytes() != new_pom.read_bytes():
        findings.append("pom.xml changed: the dynamic check runs with the base pom")
    return findings


def methods(text):
    """Test method name -> its assert lines with literals, whitespace removed."""
    result, current = {}, None
    for line in text.splitlines():
        declared = METHOD.search(line)
        if declared:
            current = declared.group(1)
            result[current] = []
        elif current and (ASSERT.search(line) or LITERAL.search(line)):
            result[current].append(re.sub(r"\s+", "", line))
    return result


def run_tests(main_from, tests_from, workdir):
    """Runs tests_from's tests against main_from's code.

    Returns {test: "failed" | "skipped" | "passed"}. Exits with code 2 when
    Maven fails and leaves no reports: the tests did not compile or run, and
    "no results" must not be read as "every test removed".
    """
    shutil.copy(main_from / "pom.xml", workdir / "pom.xml")
    shutil.copytree(main_from / MAIN_DIR, workdir / MAIN_DIR)
    if (tests_from / TEST_DIR).exists():
        shutil.copytree(tests_from / TEST_DIR, workdir / TEST_DIR)
    run = subprocess.run(["mvn", "-q", "-B", "test"], cwd=workdir,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    results = {}
    for report in (workdir / "target/surefire-reports").glob("TEST-*.xml"):
        for case in ET.parse(report).getroot().iter("testcase"):
            name = f"{case.get('classname')}.{case.get('name')}"
            if case.find("failure") is not None or case.find("error") is not None:
                results[name] = "failed"
            elif case.find("skipped") is not None:
                results[name] = "skipped"
            else:
                results[name] = "passed"
    if run.returncode != 0 and not results:
        sys.stderr.write(run.stdout[-4000:])
        print(f"guard: ERROR, tests from {tests_from} did not run against code from {main_from}")
        sys.exit(2)
    return results


def weakened_tests(base, changed):
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        before = run_tests(base, base, pathlib.Path(a))
        after = run_tests(base, changed, pathlib.Path(b))
    caught = [t for t, status in before.items() if status == "failed"]
    return [f"{t}: failed on base code before, {after.get(t, 'removed')} now"
            for t in sorted(caught) if after.get(t) != "failed"]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base, changed = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    for line in static_findings(base, changed):
        print("WARN  " + line)
    blocked = weakened_tests(base, changed)
    for line in blocked:
        print("BLOCK " + line)
    print("guard: " + ("BLOCK" if blocked else "PASS"))
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
