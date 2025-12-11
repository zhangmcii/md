===== SQL STATISTICS =====
2025-12-11 16:35:01,371 [INFO] [decorators.py:155] - Function     : get
2025-12-11 16:35:01,371 [INFO] [decorators.py:156] - Total SQL    : 8
2025-12-11 16:35:01,371 [INFO] [decorators.py:157] - SQL Time     : 0.05 sec
2025-12-11 16:35:01,371 [INFO] [decorators.py:158] - Total Time   : 0.05 sec

2025-12-11 16:35:01,371 [INFO] [decorators.py:161] - 
[1] (0.018071s)                              【这是每次jwt鉴权，都需要查询用户。省不掉】
SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.password_hash AS users_password_hash, users.confirmed AS users_confirmed, users.nickname AS users_nickname, users.location AS users_location, users.about_me AS users_about_me, users.sex AS users_sex, users.bg_image AS users_bg_image, users.member_since AS users_member_since, users.last_seen AS users_last_seen, users.image AS users_image, users.role_id AS users_role_id, users.social_account AS users_social_account, users.music AS users_music 
FROM users 
WHERE users.id = %(id_1)s 
Params: [{'id_1': 3}] 
------------------------------------------------------------
2025-12-11 16:35:01,371 [INFO] [decorators.py:161] - 
[2] (0.012661s)                               【这是每次请求更新用户上次活跃时间。省不掉】
UPDATE users SET last_seen=%(last_seen)s WHERE users.id = %(users_id)s 
Params: [{'last_seen': '2025-12-11 16:35:01', 'users_id': 3}] 
------------------------------------------------------------
2025-12-11 16:35:01,371 [INFO] [decorators.py:161] - 
[3] (0.010080s)                                 【post.id为主键，时间戳为辅助索引】 【这个 join 性能完全没有问题。】
SELECT posts.id AS posts_id, posts.body AS posts_body, posts.body_html AS posts_body_html, posts.type AS posts_type, posts.images AS posts_images, posts.timestamp AS posts_timestamp, posts.author_id AS posts_author_id, posts.deleted AS posts_deleted, users_1.id AS users_1_id, users_1.username AS users_1_username, users_1.nickname AS users_1_nickname, users_1.image AS users_1_image 
FROM posts LEFT OUTER JOIN users AS users_1 ON users_1.id = posts.author_id 
WHERE posts.deleted = false ORDER BY posts.timestamp DESC 
 LIMIT %(param_1)s, %(param_2)s 
Params: [{'param_1': 0, 'param_2': 10}] 
------------------------------------------------------------
2025-12-11 16:35:01,372 [INFO] [decorators.py:161] - 
[4] (0.001333s) 
SELECT count(*) AS count_1 
FROM (SELECT posts.id AS posts_id, posts.body AS posts_body, posts.body_html AS posts_body_html, posts.type AS posts_type, posts.images AS posts_images, posts.timestamp AS posts_timestamp, posts.author_id AS posts_author_id, posts.deleted AS posts_deleted 
FROM posts 
WHERE posts.deleted = false) AS anon_1 
Params: [{}] 
------------------------------------------------------------
2025-12-11 16:35:01,372 [INFO] [decorators.py:161] - 
[5] (0.002701s) 
SELECT images.related_id AS images_related_id, images.url AS images_url, images.`describe` AS images_describe, images.id AS images_id 
FROM images 
WHERE images.type = %(type_1)s AND images.related_id IN (%(related_id_1_1)s, %(related_id_1_2)s, %(related_id_1_3)s, %(related_id_1_4)s, %(related_id_1_5)s, %(related_id_1_6)s, %(related_id_1_7)s, %(related_id_1_8)s, %(related_id_1_9)s, %(related_id_1_10)s) ORDER BY images.related_id ASC, images.id ASC 
Params: [{'type_1': 'POST', 'related_id_1_1': 66, 'related_id_1_2': 65, 'related_id_1_3': 64, 'related_id_1_4': 63, 'related_id_1_5': 62, 'related_id_1_6': 61, 'related_id_1_7': 56, 'related_id_1_8': 54, 'related_id_1_9': 52, 'related_id_1_10': 51}] 
------------------------------------------------------------
2025-12-11 16:35:01,373 [INFO] [decorators.py:161] - 
[6] (0.001533s) 
SELECT comments.post_id AS comments_post_id, count(comments.id) AS comment_count 
FROM comments 
WHERE comments.post_id IN (%(post_id_1_1)s, %(post_id_1_2)s, %(post_id_1_3)s, %(post_id_1_4)s, %(post_id_1_5)s, %(post_id_1_6)s, %(post_id_1_7)s, %(post_id_1_8)s, %(post_id_1_9)s, %(post_id_1_10)s) GROUP BY comments.post_id 
Params: [{'post_id_1_1': 66, 'post_id_1_2': 65, 'post_id_1_3': 64, 'post_id_1_4': 63, 'post_id_1_5': 62, 'post_id_1_6': 61, 'post_id_1_7': 56, 'post_id_1_8': 54, 'post_id_1_9': 52, 'post_id_1_10': 51}] 
------------------------------------------------------------
2025-12-11 16:35:01,373 [INFO] [decorators.py:161] - 
[7] (0.003040s) 
SELECT praise.post_id AS praise_post_id, count(praise.id) AS praise_count 
FROM praise 
WHERE praise.post_id IN (%(post_id_1_1)s, %(post_id_1_2)s, %(post_id_1_3)s, %(post_id_1_4)s, %(post_id_1_5)s, %(post_id_1_6)s, %(post_id_1_7)s, %(post_id_1_8)s, %(post_id_1_9)s, %(post_id_1_10)s) GROUP BY praise.post_id 
Params: [{'post_id_1_1': 66, 'post_id_1_2': 65, 'post_id_1_3': 64, 'post_id_1_4': 63, 'post_id_1_5': 62, 'post_id_1_6': 61, 'post_id_1_7': 56, 'post_id_1_8': 54, 'post_id_1_9': 52, 'post_id_1_10': 51}] 
------------------------------------------------------------
2025-12-11 16:35:01,374 [INFO] [decorators.py:161] - 
[8] (0.000636s) 
SELECT praise.post_id AS praise_post_id 
FROM praise 
WHERE praise.post_id IN (%(post_id_1_1)s, %(post_id_1_2)s, %(post_id_1_3)s, %(post_id_1_4)s, %(post_id_1_5)s, %(post_id_1_6)s, %(post_id_1_7)s, %(post_id_1_8)s, %(post_id_1_9)s, %(post_id_1_10)s) AND praise.author_id = %(author_id_1)s 
Params: [{'author_id_1': 3, 'post_id_1_1': 66, 'post_id_1_2': 65, 'post_id_1_3': 64, 'post_id_1_4': 63, 'post_id_1_5': 62, 'post_id_1_6': 61, 'post_id_1_7': 56, 'post_id_1_8': 54, 'post_id_1_9': 52, 'post_id_1_10': 51}] 
------------------------------------------------------------
2025-12-11 16:35:01,374 [INFO] [decorators.py:162] - ==========================




## 分析第4条sql
分析的结果为：
```
Type    Key    rows     Extra
ALL     Null   59       Using where
```
### 这个执行计划代表了什么？
1. type = ALL（全表扫描）：这是最差的访问方式，表示 MySQL 必须扫描 posts 表的所有记录，然后筛选出 deleted = false 的行。
2. key = NULL ：表示查询没有使用索引。
3. rows = 59 ：表目前数据量不大，所以代价不高，但当 posts 表上百万行时，会变成灾难性性能瓶颈。
4. Extra = Using where ：说明 MySQL 做的是 “扫描所有行 → 再按 where 条件过滤”，不是走索引。

### 为什么没有用索引？
因为查询是:  
```
SELECT count(*)
FROM posts
WHERE deleted = false;
```
但 deleted 字段没有建立索引（或即使有索引，其选择性也极低 → 仍可能不走索引）。

### 这条 COUNT 查询会有什么性能问题？
1. COUNT(*) 会扫描所有 rows → 时间复杂度为O(n)
2. 无法利用索引跳过数据
3. 当表越来越大时，随着每次分页列表都要 count，会变成性能瓶颈。
例如：
* 首页展示文章列表
* 显示总条数
* 后台管理查询统计
这些操作都需要 count，一旦 posts 上百万，就会卡死。
* 
### 三、如何优化？
方案 1：给 deleted 字段加索引
如果 deleted 只有 true/false，选择性低，能否加索引要看实际比例。

当 deleted=false 是小部分时（稀疏） → 加索引有效。
若 deleted=false 是绝大部分数据 → MySQL 可能仍不走索引。

而实际项目中deleted=false的含义是"文章未被删除"， deleted=true代表"文章被删除"，显然大部分的文章都是"未被删除"状态， MySQL 会因“低选择性”对布尔字段不走索引，优化效果有限。

方案 2：使用联合索引覆盖 count 查询
如果通常按 timestamp 排序分页，那么你应该给：(deleted, timestamp) 建立联合索引，这可以：
✔ 加速 WHERE deleted 条件
✔ 加速 ORDER BY timestamp
✔ 能支持覆盖索引（无需回表）
✔ COUNT(*) 可直接在索引层统计

例如：
```
CREATE INDEX idx_posts_deleted_timestamp 
ON posts(deleted, timestamp);
```

添加索引后结果:
```
Type    Key                             rows     Extra
ref     idx_posts_deleted_timestamp     56       Using index
```


## 分析第5条sql:
分析结果：
```
Type  Key		rows 	 Extra
ALL    Null		25     	Using where; Using filesort
```

同样的问题：MySQL 必须扫描 posts 表的所有记录， 查询没有使用索引。
Using filesort --- ORDER BY 使用了文件排序，说明 ORDER BY 的列顺序不符合现有索引前缀。

你要的排序顺序刚好是 (related_id, id)，并且你过滤了 type。 因此非常适合建一个 复合索引：(type, related_id, id)
```
ALTER TABLE images
ADD INDEX idx_type_related_id_id (type, related_id, id);
```


添加索引后结果，未生效:
```
Type    Key                             rows     Extra
all     idx_type_related_id_id          25       Using where; Using filesort
```


## 分析第6，7，8条sql(形式相同):
分析结果： 
Type    Key         rows    Extra 
Range   post_id 13  Using  where; Using index

走了索引，最佳状态可