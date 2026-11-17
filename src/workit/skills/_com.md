## Late-bound COM: one rule that catches everyone

Apps reached through COM are late-bound. On most of them **a method with no arguments
is invoked just by naming it, without parentheses** (`obj.GetName`, not
`obj.GetName()`); adding `()` then fails with "... object is not callable". If you get
that error, drop the parentheses. If instead you get a bound-method object back, add
them. Methods that take arguments are always called normally.
