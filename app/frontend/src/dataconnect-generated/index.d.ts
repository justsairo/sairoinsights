import { ConnectorConfig, DataConnect, QueryRef, QueryPromise, ExecuteQueryOptions, MutationRef, MutationPromise, DataConnectSettings } from 'firebase/data-connect';

export const connectorConfig: ConnectorConfig;
export const dataConnectSettings: DataConnectSettings;

export type TimestampString = string;
export type UUIDString = string;
export type Int64String = string;
export type DateString = string;




export interface CreateProjectData {
  project_insert: Project_Key;
}

export interface CreateProjectVariables {
  title: string;
  description?: string | null;
  userId: UUIDString;
}

export interface CreateUserData {
  user_insert: User_Key;
}

export interface CreateUserVariables {
  email: string;
  displayName: string;
}

export interface DataSourceTag_Key {
  dataSourceId: UUIDString;
  tagId: UUIDString;
  __typename?: 'DataSourceTag_Key';
}

export interface DataSource_Key {
  id: UUIDString;
  __typename?: 'DataSource_Key';
}

export interface DeleteReportData {
  report_delete?: Report_Key | null;
}

export interface DeleteReportVariables {
  id: UUIDString;
}

export interface ListUserProjectsData {
  projects: ({
    id: UUIDString;
    title: string;
    description?: string | null;
  } & Project_Key)[];
}

export interface ListUserProjectsVariables {
  userId: UUIDString;
}

export interface Metric_Key {
  id: UUIDString;
  __typename?: 'Metric_Key';
}

export interface Project_Key {
  id: UUIDString;
  __typename?: 'Project_Key';
}

export interface Report_Key {
  id: UUIDString;
  __typename?: 'Report_Key';
}

export interface Tag_Key {
  id: UUIDString;
  __typename?: 'Tag_Key';
}

export interface User_Key {
  id: UUIDString;
  __typename?: 'User_Key';
}

interface CreateUserRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateUserVariables): MutationRef<CreateUserData, CreateUserVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateUserVariables): MutationRef<CreateUserData, CreateUserVariables>;
  operationName: string;
}
export const createUserRef: CreateUserRef;

export function createUser(vars: CreateUserVariables): MutationPromise<CreateUserData, CreateUserVariables>;
export function createUser(dc: DataConnect, vars: CreateUserVariables): MutationPromise<CreateUserData, CreateUserVariables>;

interface CreateProjectRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateProjectVariables): MutationRef<CreateProjectData, CreateProjectVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateProjectVariables): MutationRef<CreateProjectData, CreateProjectVariables>;
  operationName: string;
}
export const createProjectRef: CreateProjectRef;

export function createProject(vars: CreateProjectVariables): MutationPromise<CreateProjectData, CreateProjectVariables>;
export function createProject(dc: DataConnect, vars: CreateProjectVariables): MutationPromise<CreateProjectData, CreateProjectVariables>;

interface ListUserProjectsRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListUserProjectsVariables): QueryRef<ListUserProjectsData, ListUserProjectsVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: ListUserProjectsVariables): QueryRef<ListUserProjectsData, ListUserProjectsVariables>;
  operationName: string;
}
export const listUserProjectsRef: ListUserProjectsRef;

export function listUserProjects(vars: ListUserProjectsVariables, options?: ExecuteQueryOptions): QueryPromise<ListUserProjectsData, ListUserProjectsVariables>;
export function listUserProjects(dc: DataConnect, vars: ListUserProjectsVariables, options?: ExecuteQueryOptions): QueryPromise<ListUserProjectsData, ListUserProjectsVariables>;

interface DeleteReportRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteReportVariables): MutationRef<DeleteReportData, DeleteReportVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: DeleteReportVariables): MutationRef<DeleteReportData, DeleteReportVariables>;
  operationName: string;
}
export const deleteReportRef: DeleteReportRef;

export function deleteReport(vars: DeleteReportVariables): MutationPromise<DeleteReportData, DeleteReportVariables>;
export function deleteReport(dc: DataConnect, vars: DeleteReportVariables): MutationPromise<DeleteReportData, DeleteReportVariables>;

