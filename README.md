# Pratt parsing versus Shunting Yard

This is the code leftovers from an experiment into how similar Pratt
parsing and the shunting yard algorithm really are. Maybe at some
point there will be a more comprehensive writeup/blog post on this,
but for now it's just this and a collection of code artifacts.

## What I did

I implemented a Pratt parser in python based on [this blog
post](https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html)
which implemented one in rust. The language I chose was a simple one
that's a subset of what python allows for numeric expressions. I also
implemented a shunting yard-based parser for the same language, and
drove both with the same table of operator precedence.

The shunting yard parser uses a standard variation with a token state
that alternates between two values to track whether we expect an
operator next or an atom. It also uses a quirk I've used in the past
where values are not shoved onto the output queue/executed
immediately, but are instead nodes of the highest priority on the
operator stack.

These are the files `basic_pratt.py` and `shunting_yard.py` supported
by the base library file `op_base.py` which contains definitions for
my AST classes, the table of operator precedence, and my simple
single-regex-based lexer.

I made both parsers recognize exactly the same language, including
producing identical errors in all the possible error cases, and added
a unit test to keep myself honest.

I then began a series of experiments to transform the Pratt parser
into the shunting yard parser based on the idea that if you squint at
it, shunting yard sort of looks like a standard stackless
transformation of Pratt parsing.

It wasn't quite that simple to show the two algorithms equivalent.

In fact, there are at least three significant changes that need to
happen to go from Pratt parsing to the shunting yard algorithm:

* The parser must be transformed to be made non-recursive with an
  explicitly managed stack.
* The parser must be changed to only call poll() on the lexer, and
  never peek()
* The parser must be made to keep intermediate values on a separate
  stack, not in the local `lhs` and `rhs` variables.

The other files represent stages in the transformation from
`basic_pratt` to `shunting_yard`: first `basic_pratt` becomes
`pratt_nopeek`, then `pratt_stackless`, then `prat_stackless2`,
`pratt_stackless3`, ... and finally `pratt_stackless9`, which is as
close to `shunting_yard` as one can get without keeping intermediate
values in a separate value stack.

To show that the transformation to keep values in a separate stack is
independent of the other transformations, I also have
`pratt_returnless` which is just `basic_pratt` with that
transformation.

To run the unit test, from the directory with this file in it, run
`python -m unittest`; interactive testing can be done with `python -m
pratt_v_syard`.
