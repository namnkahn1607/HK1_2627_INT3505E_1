### 1. Xác định resources trong miền

- `posts`, `users`, `comments`, `tags` là resource.
- `profile` là singleton sub-resource, có quan hệ 1-1 với mỗi user.
- `follow` không phải là resource thật, mà thực chất nó là quan hệ giữa user-user.

### 2. Phân loại collection / item / sub-resource

| Loại | Resource | URI |
|---|---|---|
| Collection | posts, users, tags | `/posts`, `/users`, `/tags` |
| Item | post, user, comment | `/posts/{id}`, `/users/{id}`, `/comments/{id}` |
| Sub-collection | comments của post | `/posts/{id}/comments` |
| Singleton sub-resource | profile của user | `/users/{id}/profile` |
| Relationship | tag <-> post, user -> user | `/posts/{id}/tags/{tag}`, `/users/{id}/following/{target}` |

### 3. Vẽ sơ đồ cây endpoint và quyết định version segment

```
/api/v1
├── /posts
│   └── /{post_id}
│       ├── /comments
│       └── /tags
│           └── /{tag}
├── /comments
│   └── /{comment_id}
├── /tags
└── /users
    └── /{user_id}
        ├── /profile
        ├── /following
        │   └── /{target_id}
        └── /followers
```
