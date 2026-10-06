### 1. Xác định resources trong miền

- `posts`, `users`, `comments`, `tags` là resource.
- `profile` là singleton sub-resource, có quan hệ 1-1 với mỗi user.
- `follow` không phải là resource thật, mà thực chất nó là quan hệ giữa user-user.
