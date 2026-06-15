import { ConnectorConfig, DataConnect, QueryRef, QueryPromise, ExecuteQueryOptions, MutationRef, MutationPromise, DataConnectSettings } from 'firebase/data-connect';

export const connectorConfig: ConnectorConfig;
export const dataConnectSettings: DataConnectSettings;

export type TimestampString = string;
export type UUIDString = string;
export type Int64String = string;
export type DateString = string;




export interface Account_Key {
  id: UUIDString;
  __typename?: 'Account_Key';
}

export interface Content_Key {
  id: UUIDString;
  __typename?: 'Content_Key';
}

export interface CreateAccountData {
  account_insert: Account_Key;
}

export interface CreateAccountVariables {
  platformName: string;
  externalAccountId: string;
}

export interface GetUserProfileData {
  user?: {
    displayName: string;
    email: string;
    subscriptionTier?: string | null;
  };
}

export interface Insight_Key {
  id: UUIDString;
  __typename?: 'Insight_Key';
}

export interface ListInsightsData {
  insights: ({
    title: string;
    description: string;
    priorityLevel: number;
    isActioned?: boolean | null;
  })[];
}

export interface LogMetricData {
  metric_insert: Metric_Key;
}

export interface LogMetricVariables {
  contentId: UUIDString;
  metricType: string;
  value: number;
}

export interface Metric_Key {
  id: UUIDString;
  __typename?: 'Metric_Key';
}

export interface User_Key {
  id: UUIDString;
  __typename?: 'User_Key';
}

interface GetUserProfileRef {
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<GetUserProfileData, undefined>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect): QueryRef<GetUserProfileData, undefined>;
  operationName: string;
}
export const getUserProfileRef: GetUserProfileRef;

export function getUserProfile(options?: ExecuteQueryOptions): QueryPromise<GetUserProfileData, undefined>;
export function getUserProfile(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<GetUserProfileData, undefined>;

interface CreateAccountRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateAccountVariables): MutationRef<CreateAccountData, CreateAccountVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateAccountVariables): MutationRef<CreateAccountData, CreateAccountVariables>;
  operationName: string;
}
export const createAccountRef: CreateAccountRef;

export function createAccount(vars: CreateAccountVariables): MutationPromise<CreateAccountData, CreateAccountVariables>;
export function createAccount(dc: DataConnect, vars: CreateAccountVariables): MutationPromise<CreateAccountData, CreateAccountVariables>;

interface LogMetricRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: LogMetricVariables): MutationRef<LogMetricData, LogMetricVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: LogMetricVariables): MutationRef<LogMetricData, LogMetricVariables>;
  operationName: string;
}
export const logMetricRef: LogMetricRef;

export function logMetric(vars: LogMetricVariables): MutationPromise<LogMetricData, LogMetricVariables>;
export function logMetric(dc: DataConnect, vars: LogMetricVariables): MutationPromise<LogMetricData, LogMetricVariables>;

interface ListInsightsRef {
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListInsightsData, undefined>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect): QueryRef<ListInsightsData, undefined>;
  operationName: string;
}
export const listInsightsRef: ListInsightsRef;

export function listInsights(options?: ExecuteQueryOptions): QueryPromise<ListInsightsData, undefined>;
export function listInsights(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<ListInsightsData, undefined>;

