# Generated TypeScript README
This README will guide you through the process of using the generated JavaScript SDK package for the connector `example`. It will also provide examples on how to use your generated SDK to call your Data Connect queries and mutations.

***NOTE:** This README is generated alongside the generated SDK. If you make changes to this file, they will be overwritten when the SDK is regenerated.*

# Table of Contents
- [**Overview**](#generated-javascript-readme)
- [**Accessing the connector**](#accessing-the-connector)
  - [*Connecting to the local Emulator*](#connecting-to-the-local-emulator)
- [**Queries**](#queries)
  - [*GetUserProfile*](#getuserprofile)
  - [*ListInsights*](#listinsights)
- [**Mutations**](#mutations)
  - [*CreateAccount*](#createaccount)
  - [*LogMetric*](#logmetric)

# Accessing the connector
A connector is a collection of Queries and Mutations. One SDK is generated for each connector - this SDK is generated for the connector `example`. You can find more information about connectors in the [Data Connect documentation](https://firebase.google.com/docs/data-connect#how-does).

You can use this generated SDK by importing from the package `@dataconnect/generated` as shown below. Both CommonJS and ESM imports are supported.

You can also follow the instructions from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#set-client).

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig } from '@dataconnect/generated';

const dataConnect = getDataConnect(connectorConfig);
```

## Connecting to the local Emulator
By default, the connector will connect to the production service.

To connect to the emulator, you can use the following code.
You can also follow the emulator instructions from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#instrument-clients).

```typescript
import { connectDataConnectEmulator, getDataConnect } from 'firebase/data-connect';
import { connectorConfig } from '@dataconnect/generated';

const dataConnect = getDataConnect(connectorConfig);
connectDataConnectEmulator(dataConnect, 'localhost', 9399);
```

After it's initialized, you can call your Data Connect [queries](#queries) and [mutations](#mutations) from your generated SDK.

# Queries

There are two ways to execute a Data Connect Query using the generated Web SDK:
- Using a Query Reference function, which returns a `QueryRef`
  - The `QueryRef` can be used as an argument to `executeQuery()`, which will execute the Query and return a `QueryPromise`
- Using an action shortcut function, which returns a `QueryPromise`
  - Calling the action shortcut function will execute the Query and return a `QueryPromise`

The following is true for both the action shortcut function and the `QueryRef` function:
- The `QueryPromise` returned will resolve to the result of the Query once it has finished executing
- If the Query accepts arguments, both the action shortcut function and the `QueryRef` function accept a single argument: an object that contains all the required variables (and the optional variables) for the Query
- Both functions can be called with or without passing in a `DataConnect` instance as an argument. If no `DataConnect` argument is passed in, then the generated SDK will call `getDataConnect(connectorConfig)` behind the scenes for you.

Below are examples of how to use the `example` connector's generated functions to execute each query. You can also follow the examples from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#using-queries).

## GetUserProfile
You can execute the `GetUserProfile` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getUserProfile(options?: ExecuteQueryOptions): QueryPromise<GetUserProfileData, undefined>;

interface GetUserProfileRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<GetUserProfileData, undefined>;
}
export const getUserProfileRef: GetUserProfileRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getUserProfile(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<GetUserProfileData, undefined>;

interface GetUserProfileRef {
  ...
  (dc: DataConnect): QueryRef<GetUserProfileData, undefined>;
}
export const getUserProfileRef: GetUserProfileRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getUserProfileRef:
```typescript
const name = getUserProfileRef.operationName;
console.log(name);
```

### Variables
The `GetUserProfile` query has no variables.
### Return Type
Recall that executing the `GetUserProfile` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetUserProfileData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface GetUserProfileData {
  user?: {
    displayName: string;
    email: string;
    subscriptionTier?: string | null;
  };
}
```
### Using `GetUserProfile`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getUserProfile } from '@dataconnect/generated';


// Call the `getUserProfile()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getUserProfile();

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getUserProfile(dataConnect);

console.log(data.user);

// Or, you can use the `Promise` API.
getUserProfile().then((response) => {
  const data = response.data;
  console.log(data.user);
});
```

### Using `GetUserProfile`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getUserProfileRef } from '@dataconnect/generated';


// Call the `getUserProfileRef()` function to get a reference to the query.
const ref = getUserProfileRef();

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getUserProfileRef(dataConnect);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.user);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.user);
});
```

## ListInsights
You can execute the `ListInsights` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listInsights(options?: ExecuteQueryOptions): QueryPromise<ListInsightsData, undefined>;

interface ListInsightsRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListInsightsData, undefined>;
}
export const listInsightsRef: ListInsightsRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listInsights(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<ListInsightsData, undefined>;

interface ListInsightsRef {
  ...
  (dc: DataConnect): QueryRef<ListInsightsData, undefined>;
}
export const listInsightsRef: ListInsightsRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listInsightsRef:
```typescript
const name = listInsightsRef.operationName;
console.log(name);
```

### Variables
The `ListInsights` query has no variables.
### Return Type
Recall that executing the `ListInsights` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListInsightsData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface ListInsightsData {
  insights: ({
    title: string;
    description: string;
    priorityLevel: number;
    isActioned?: boolean | null;
  })[];
}
```
### Using `ListInsights`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listInsights } from '@dataconnect/generated';


// Call the `listInsights()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listInsights();

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listInsights(dataConnect);

console.log(data.insights);

// Or, you can use the `Promise` API.
listInsights().then((response) => {
  const data = response.data;
  console.log(data.insights);
});
```

### Using `ListInsights`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listInsightsRef } from '@dataconnect/generated';


// Call the `listInsightsRef()` function to get a reference to the query.
const ref = listInsightsRef();

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listInsightsRef(dataConnect);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.insights);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.insights);
});
```

# Mutations

There are two ways to execute a Data Connect Mutation using the generated Web SDK:
- Using a Mutation Reference function, which returns a `MutationRef`
  - The `MutationRef` can be used as an argument to `executeMutation()`, which will execute the Mutation and return a `MutationPromise`
- Using an action shortcut function, which returns a `MutationPromise`
  - Calling the action shortcut function will execute the Mutation and return a `MutationPromise`

The following is true for both the action shortcut function and the `MutationRef` function:
- The `MutationPromise` returned will resolve to the result of the Mutation once it has finished executing
- If the Mutation accepts arguments, both the action shortcut function and the `MutationRef` function accept a single argument: an object that contains all the required variables (and the optional variables) for the Mutation
- Both functions can be called with or without passing in a `DataConnect` instance as an argument. If no `DataConnect` argument is passed in, then the generated SDK will call `getDataConnect(connectorConfig)` behind the scenes for you.

Below are examples of how to use the `example` connector's generated functions to execute each mutation. You can also follow the examples from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#using-mutations).

## CreateAccount
You can execute the `CreateAccount` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createAccount(vars: CreateAccountVariables): MutationPromise<CreateAccountData, CreateAccountVariables>;

interface CreateAccountRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateAccountVariables): MutationRef<CreateAccountData, CreateAccountVariables>;
}
export const createAccountRef: CreateAccountRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createAccount(dc: DataConnect, vars: CreateAccountVariables): MutationPromise<CreateAccountData, CreateAccountVariables>;

interface CreateAccountRef {
  ...
  (dc: DataConnect, vars: CreateAccountVariables): MutationRef<CreateAccountData, CreateAccountVariables>;
}
export const createAccountRef: CreateAccountRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createAccountRef:
```typescript
const name = createAccountRef.operationName;
console.log(name);
```

### Variables
The `CreateAccount` mutation requires an argument of type `CreateAccountVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface CreateAccountVariables {
  platformName: string;
  externalAccountId: string;
}
```
### Return Type
Recall that executing the `CreateAccount` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateAccountData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateAccountData {
  account_insert: Account_Key;
}
```
### Using `CreateAccount`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createAccount, CreateAccountVariables } from '@dataconnect/generated';

// The `CreateAccount` mutation requires an argument of type `CreateAccountVariables`:
const createAccountVars: CreateAccountVariables = {
  platformName: ..., 
  externalAccountId: ..., 
};

// Call the `createAccount()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createAccount(createAccountVars);
// Variables can be defined inline as well.
const { data } = await createAccount({ platformName: ..., externalAccountId: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createAccount(dataConnect, createAccountVars);

console.log(data.account_insert);

// Or, you can use the `Promise` API.
createAccount(createAccountVars).then((response) => {
  const data = response.data;
  console.log(data.account_insert);
});
```

### Using `CreateAccount`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createAccountRef, CreateAccountVariables } from '@dataconnect/generated';

// The `CreateAccount` mutation requires an argument of type `CreateAccountVariables`:
const createAccountVars: CreateAccountVariables = {
  platformName: ..., 
  externalAccountId: ..., 
};

// Call the `createAccountRef()` function to get a reference to the mutation.
const ref = createAccountRef(createAccountVars);
// Variables can be defined inline as well.
const ref = createAccountRef({ platformName: ..., externalAccountId: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createAccountRef(dataConnect, createAccountVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.account_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.account_insert);
});
```

## LogMetric
You can execute the `LogMetric` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
logMetric(vars: LogMetricVariables): MutationPromise<LogMetricData, LogMetricVariables>;

interface LogMetricRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: LogMetricVariables): MutationRef<LogMetricData, LogMetricVariables>;
}
export const logMetricRef: LogMetricRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
logMetric(dc: DataConnect, vars: LogMetricVariables): MutationPromise<LogMetricData, LogMetricVariables>;

interface LogMetricRef {
  ...
  (dc: DataConnect, vars: LogMetricVariables): MutationRef<LogMetricData, LogMetricVariables>;
}
export const logMetricRef: LogMetricRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the logMetricRef:
```typescript
const name = logMetricRef.operationName;
console.log(name);
```

### Variables
The `LogMetric` mutation requires an argument of type `LogMetricVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface LogMetricVariables {
  contentId: UUIDString;
  metricType: string;
  value: number;
}
```
### Return Type
Recall that executing the `LogMetric` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `LogMetricData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface LogMetricData {
  metric_insert: Metric_Key;
}
```
### Using `LogMetric`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, logMetric, LogMetricVariables } from '@dataconnect/generated';

// The `LogMetric` mutation requires an argument of type `LogMetricVariables`:
const logMetricVars: LogMetricVariables = {
  contentId: ..., 
  metricType: ..., 
  value: ..., 
};

// Call the `logMetric()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await logMetric(logMetricVars);
// Variables can be defined inline as well.
const { data } = await logMetric({ contentId: ..., metricType: ..., value: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await logMetric(dataConnect, logMetricVars);

console.log(data.metric_insert);

// Or, you can use the `Promise` API.
logMetric(logMetricVars).then((response) => {
  const data = response.data;
  console.log(data.metric_insert);
});
```

### Using `LogMetric`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, logMetricRef, LogMetricVariables } from '@dataconnect/generated';

// The `LogMetric` mutation requires an argument of type `LogMetricVariables`:
const logMetricVars: LogMetricVariables = {
  contentId: ..., 
  metricType: ..., 
  value: ..., 
};

// Call the `logMetricRef()` function to get a reference to the mutation.
const ref = logMetricRef(logMetricVars);
// Variables can be defined inline as well.
const ref = logMetricRef({ contentId: ..., metricType: ..., value: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = logMetricRef(dataConnect, logMetricVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.metric_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.metric_insert);
});
```

