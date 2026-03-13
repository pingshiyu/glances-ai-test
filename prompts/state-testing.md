Look into the <state-testing-section> of the file `prompts/state-based-testing-overview.md`. 

**Environment:** To run the system under test (SUT) with all dependencies satisfied, activate the SUT environment first (see **SUT environment** in `state_testing/README.md`): create and activate `.venv-sut` (e.g. `python -m venv .venv-sut` then `source .venv-sut/bin/activate` and `pip install -e .` from the project root).

I would like to build a state-based fuzzer for the public calls in component <state-testing-section>, whilst at the same time empirically inferring a semantics for the API of this component, which act as documentation.
The semantics should describe the pre and postconditions of the calls in the API, with respect to some abstraction that the semantics can refer to in the pre/postconditions.

Step 1. Documentation preparation 
Examine the component in section <state-testing-section>. 
Then _infer_, roughly, what should be the semantics of the functions. The semantics can refer to abstract states. 
Write the above semantics into a document, called the _initial_ semantics (of the component <state-testing-section>). It should include the public calls within the library, and also how the function should behave according to the semantics. This document should stay fixed and not change. Copy the initial document into another, to act as the  _working_ semantics, which we are going to modify iteratively in the below process.
If there are higher-order functions in this part of the API, please highlight these in the initial document.

The _initial_ document MUST NOT BE CHANGED AFTER STEP 1.

Step 2: State based fuzzer creation / modification.
You should write a fuzzer that:
- for each public API calls in the component, there should be a corresponding function in the fuzzer that executes the API call.
- use the testing module in the `state_testing` folder to define generators that can be run, where you need to supply the input generators to the functions
- to ensure the inputs meet the preconditions of the calls, you should define new generators (which can reference the abstract state, e.g. within a class that defines and maintains the abstract state, the generators, and wrappers to API calls that also maintains the abstract state in the postcondition) that produce outputs that satisfies preconditions only. Ensure the output of the generators has good coverage of the input space, and covers the edge cases. You may modify the definition of the abstract state to make defining generators more convenient, but keep these changes up-to-date in the semantics file.
- the call should maintain the abstract state of the function, so that after each call, the abstract state is updated to reflect the post-call state.

Step 3: Execute the fuzzer.
- collect the executors defined before into a list, and define an initial state to begin testing (the initial state can be random too if there are many reasonable initial states)
- run the test harness to execute at random for ~1,000 iterations (this code will be defined)

If there are any crashes, record these down in your documentation in a separate section, and decide whethe the crash is due to a bug in the API, or is it due to an issue in the fuzzer (the preconditions does not reflect the constraints in the code, or the abstract state has gone out of sync with the concrete state during execution).
- If the issue is in the API: record this down as a bug in the document, and continue testing. Comment out the bug-triggering function temporarily.
- If the issue is in the fuzzer: investigate the root cause of the issue, and update the pre/post conditions if necessary, keeping the _working_ document up-to-date with your changes.


Return to step 2, and continue the development loop until either all executors are commented out, or when the long-running fuzzer finishes without errors.

Development notes:
The fuzzer should avoid using `try/catch` to absorb errors as much as possible: the non-crashing behaviour should be from generating the correct inputs for the function. 

Ensure you cover as much of the public functions of the API as possible. 
If any functions are not possible/infeasible to cover, please document these with reasons why.

The task for the agnet is to create the files:
- `<state-testing-section>_entry.py` - contains the entry point: it should contain the "dummyTester" function, defined as in the existing examples, and run the fuzzer in a loop for 1000 iterations. 
- `<state-testing-section>_generators.py` - contains the actual random generator and calls to the libraries.
- `<state-testing-section>_lib.py` - contains the defined executors: the function along with their generators.

The success criterion for a fuzzer is that running the fuzzer in a loop for 1000 iterations should pass without errors.

At the end of the task, please also document the overall structure of the fuzzer, the design decisions made and their reasoning (from what has been discovered during development).
The document should be detailed enough to inform another agent, and humans, of how it was implemented, and allow another agent/human to reimplement the fuzzer, sidestepping the common mistakes that may occur.