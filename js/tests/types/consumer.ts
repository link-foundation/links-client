import {
  AuthStorageService,
  ILinks,
  LinkDBService,
  MenuStorageService,
  RecursiveLinks,
  type Link,
  type MenuItem,
} from '../../src/index.js';

const db = new LinkDBService('/tmp/example.links');
const created: Promise<Link> = db.createLink(1, 2);
const found: Promise<Link | null> = db.readLink(1);

const menu: MenuItem[] = [{ label: 'Home', to: '/', items: [{ label: 'Child' }] }];
const menuStorage = new MenuStorageService();
const menuIds: Promise<number[]> = menuStorage.storeMenuStructure(menu);

const auth = new AuthStorageService();
const userId: Promise<string> = auth.createUser({ username: 'alice' }).then(user => user.userId);

const links = new ILinks();
const count: Promise<number> = links.count([0, 1, 2]);
const recursive = new RecursiveLinks();
const notation: string = recursive.toLinksNotation([[1, 2], [3, 4]]);

void [created, found, menuIds, userId, count, notation];
