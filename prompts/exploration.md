I am looking to apply a testing methodology to this codebase, intended to be applied to individual components. 

The testing will be based on a randomised state-based input generator, where the agent will write functions to randomly execute the public API of the component. 
The agent will write the random input generators and specify the (generator, function API) definitions for the executors.
The executors will be run at random, for a long run (e.g. 1000+ iterations). Crashes will be investigated to see whether they came from
- an incorrect assumption of the preconditions of the function
- a bug in the implementation (where the precondition assumption is correct)

Through this process, the agent would simultaneously refine a specification of the API, and also find bugs in the API - in a way that is backed up by real executions.

That is the setting for how we plan to do testing.
Your task for this step is to explore the codebase and find the components for which this methodology is suitable for application. 