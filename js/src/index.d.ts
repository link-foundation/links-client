export interface Link {
  id: number;
  source: number;
  target: number;
}

export interface QueryOptions {
  before?: boolean;
  changes?: boolean;
  after?: boolean;
  trace?: boolean;
}

export interface MenuItem {
  label?: string;
  icon?: string;
  to?: string;
  items?: MenuItem[];
  [key: string]: unknown;
}

export interface StoredMenuItem extends MenuItem {
  _linkId: number;
  _itemId: number;
  _parentId?: number;
  items?: StoredMenuItem[];
}

export interface UserData {
  username?: string;
  email?: string;
  profile?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface StoredUser extends UserData {
  userId: string;
  createdAt: string;
  updatedAt?: string;
}

export interface TokenData {
  apiKey?: string;
  permissions?: string[];
  expiresAt?: string;
  [key: string]: unknown;
}

export interface StoredToken extends TokenData {
  tokenId: string;
  userId: string;
  createdAt: string;
}

export interface PasswordData {
  hash: string;
  salt: string;
  algorithm?: string;
  iterations?: number;
  [key: string]: unknown;
}

export interface StoredPassword extends PasswordData {
  passwordId: string;
  userId: string;
  createdAt: string;
}

export interface StorageStatistics {
  totalLinks: number;
  users: { links: number; files: number };
  tokens: { links: number; files: number };
  passwords: { files: number };
}

export class LinkDBService {
  constructor(dbPath?: string);
  dbPath: string;
  nextId: number;
  executeQuery(query: string, options?: QueryOptions): Promise<string>;
  parseLinks(output: string): Link[];
  createLink(source: number, target: number): Promise<Link>;
  readAllLinks(): Promise<Link[]>;
  readLink(id: number): Promise<Link | null>;
  updateLink(id: number, newSource: number, newTarget: number): Promise<Link>;
  deleteLink(id: number): Promise<boolean>;
  storeMenuItem(menuItem: MenuItem): Promise<number>;
  getAllMenuItems(): Promise<Link[]>;
  deleteMenuItem(linkId: number): Promise<boolean>;
  clearDatabase(): Promise<boolean>;
}

export class MenuStorageService {
  constructor();
  linkDB: LinkDBService;
  ensureDataDirectory(): Promise<void>;
  generateItemId(item: MenuItem): number;
  saveItemData(itemId: number, item: MenuItem): Promise<void>;
  loadItemData(itemId: number): Promise<MenuItem | null>;
  storeMenuItem(item: MenuItem, parentId?: number): Promise<number>;
  storeMenuStructure(menuItems: MenuItem[], parentId?: number): Promise<number[]>;
  getMenuStructure(parentId?: number): Promise<StoredMenuItem[]>;
  getAllMenuItems(): Promise<StoredMenuItem[]>;
  deleteMenuItem(itemId: number): Promise<boolean>;
  clearAllMenus(): Promise<boolean>;
  getStatistics(): Promise<{ totalLinks: number; totalFiles: number; rootItems: number }>;
}

export class AuthStorageService {
  constructor();
  linkDB: LinkDBService;
  ensureDataDirectories(): Promise<void>;
  generateId(content: object, prefix?: string): string;
  idToNumber(id: string): number;
  saveData(dir: string, id: string, data: object): Promise<void>;
  loadData(dir: string, id: string): Promise<Record<string, unknown> | null>;
  createUser(userData: UserData): Promise<StoredUser>;
  getUser(userId: string): Promise<StoredUser | null>;
  getAllUsers(): Promise<StoredUser[]>;
  updateUser(userId: string, updates: Partial<UserData>): Promise<StoredUser>;
  deleteUser(userId: string): Promise<boolean>;
  createToken(userId: string, tokenData: TokenData): Promise<StoredToken>;
  getToken(tokenId: string): Promise<StoredToken | null>;
  getUserTokens(userId: string): Promise<StoredToken[]>;
  deleteToken(tokenId: string): Promise<boolean>;
  setPassword(userId: string, passwordData: PasswordData): Promise<StoredPassword>;
  getUserPassword(userId: string): Promise<StoredPassword | null>;
  getUserPasswords(userId: string): Promise<StoredPassword[]>;
  deletePassword(passwordId: string): Promise<boolean>;
  getStatistics(): Promise<StorageStatistics>;
  clearAllAuthData(): Promise<boolean>;
  findUserByUsername(username: string): Promise<StoredUser | null>;
  findUserByEmail(email: string): Promise<StoredUser | null>;
  findTokenByApiKey(apiKey: string): Promise<StoredToken | null>;
}

export interface LinksConstants {
  Continue: symbol;
  Break: symbol;
  Any: 0;
}

export type LinkRestriction = readonly number[];
export type LinkSubstitution = readonly [number, number] | readonly [number, number, number];
export type LinkHandler = (link: Link) => symbol | void | Promise<symbol | void>;
export interface LinkChange { before: Link | null; after: Link | null }
export type LinkChangeHandler = (change: LinkChange) => void | Promise<void>;

export class ILinks {
  constructor(dbPath?: string | null);
  db: LinkDBService;
  constants: LinksConstants;
  getConstants(): LinksConstants;
  count(restriction?: LinkRestriction | null): Promise<number>;
  each(restriction?: LinkRestriction | null, handler?: LinkHandler | null): Promise<symbol>;
  create(substitution: LinkSubstitution, handler?: LinkChangeHandler | null): Promise<number>;
  update(restriction: LinkRestriction, substitution: LinkSubstitution, handler?: LinkChangeHandler | null): Promise<number>;
  delete(restriction: LinkRestriction, handler?: LinkChangeHandler | null): Promise<number>;
}

export type NestedLinkValue = number | NestedLinkArray | NestedLinkObject;
export type NestedLinkArray = NestedLinkValue[];
export type NestedLinkObject = { [reference: string]: NestedLinkArray };

export class RecursiveLinks {
  constructor(dbPath?: string | null);
  links: ILinks;
  idCounter: number;
  getLinks(): ILinks;
  createFromNestedArray(nestedArray: NestedLinkArray[]): Promise<number[]>;
  createFromNestedObject(nestedObject: NestedLinkObject): Promise<Record<string, number>>;
  readAsNestedArray(restriction?: LinkRestriction | null): Promise<number[][]>;
  toLinksNotation(input: NestedLinkArray | NestedLinkObject | number): string;
  parseLinksNotation(notation: string): NestedLinkArray;
}

export interface Logger {
  debug(contextOrMessage: unknown, message?: string): void;
  info(contextOrMessage: unknown, message?: string): void;
  warn(contextOrMessage: unknown, message?: string): void;
  error(contextOrMessage: unknown, message?: string): void;
}

export const logger: Logger;

/** Express router factory. The return type is structural to avoid requiring @types/express. */
export function menuConfigRoutes(): { use: (...args: unknown[]) => unknown };
export const authDataRoutes: { use: (...args: unknown[]) => unknown };
