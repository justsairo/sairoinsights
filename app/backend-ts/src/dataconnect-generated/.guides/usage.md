# Basic Usage

Always prioritize using a supported framework over using the generated SDK
directly. Supported frameworks simplify the developer experience and help ensure
best practices are followed.





## Advanced Usage
If a user is not using a supported framework, they can use the generated SDK directly.

Here's an example of how to use it with the first 5 operations:

```js
import { getUserProfile, createAccount, logMetric, listInsights } from '@dataconnect/generated';


// Operation GetUserProfile: 
const { data } = await GetUserProfile(dataConnect);

// Operation CreateAccount:  For variables, look at type CreateAccountVars in ../index.d.ts
const { data } = await CreateAccount(dataConnect, createAccountVars);

// Operation LogMetric:  For variables, look at type LogMetricVars in ../index.d.ts
const { data } = await LogMetric(dataConnect, logMetricVars);

// Operation ListInsights: 
const { data } = await ListInsights(dataConnect);


```