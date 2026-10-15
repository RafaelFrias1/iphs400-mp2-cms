# CMS Content Model, Roles, and Publishing: Research Notes

## Summary

WordPress, Drupal, and static-site generators (SSGs) represent three distinct content management paradigms. WordPress and Drupal are dynamic, database-backed systems that render content per request using roles and capabilities to manage user access; WordPress uses a flat post-type model with post metadata and taxonomies, while Drupal uses a more flexible entity/bundle/field system. SSGs (Hugo, Jekyll) are build-time systems that store content as flat files with YAML/TOML metadata and produce static HTML; they have no runtime user model. All three support drafts, revisions, and publishing workflows, but the mechanisms differ: WordPress uses post statuses (draft, publish, pending, future, private), Drupal uses a published flag with optional Content Moderation workflows, and SSGs use file locations (\_drafts) and front-matter metadata (draft: true, published: false). Understanding these models is essential for designing a hybrid system like IPHS 400's local admin + static-publish CMS.

---

## Glossary

| **Term** | **Definition** | **WordPress** | **Drupal** | **SSG** |
|----------|---|---|---|---|
| **Content Type** | Classification of content with its own fields and behavior | Post types (post, page, custom) | Content types (bundles of entity types) | File type determined by directory (e.g., posts/, pages/) |
| **Bundle** | Sub-type or variant of a content type | Not explicitly called "bundle"; implicit in post types | Formal concept; entity subtype with shared fields | Not applicable (SSGs don't have runtime bundles) |
| **Slug** | Human-readable URL component derived from title | Postname field; can be customized | Path alias; Drupal term for URL component | Filename (with optional slug override in front matter) |
| **Draft / Published** | Post status states | Draft (status='draft'), publish (status='publish') | Published flag (boolean; not status) | File in \_drafts/ folder, or draft: true in front matter |
| **Post Status** | State of a post in its lifecycle | 8 built-in: publish, draft, pending, future, private, trash, auto-draft, inherit | Published (boolean) + optional Content Moderation states | Built-time flag; no runtime status |
| **Role** | User classification determining permissions | 6 default: Super Admin, Administrator, Editor, Author, Contributor, Subscriber | Named roles (anonymous, authenticated, custom) | No runtime users (access via git/filesystem) |
| **Capability / Permission** | Specific action a role can perform | Capabilities are properties of roles (e.g., edit_posts, publish_posts) | Permissions assigned to roles (e.g., "create node") | Not applicable (static output, no runtime access control) |
| **Permalink** | Permanent URL of published content | Post URL; determined by post type, slug, and date structure | Entity URL; determined by path alias and entity ID | Static URL determined by directory and slug at build time |
| **Taxonomy** | Classification system for organizing content | Hierarchical (categories) and flat (tags); custom taxonomies supported | Vocabulary with terms; flexible and hierarchical | Taxonomies: custom flat or hierarchical classification in front matter |
| **Field / Post Meta** | Data attached to content items | Post meta (postmeta table); unstructured key-value pairs | Fields (structured, with type definitions) attached to bundles | Front matter metadata (YAML/TOML key-value pairs) |
| **Revision** | Saved version of content; allows undo/restore | Stored in posts table with post_type='revision'; automatic autosaves | Entity revision; core supports revisions on all content entities | Git history or manual version control in source files |
| **Theme** | Design and layout layer | PHP template files, CSS, and assets; renders posts/pages dynamically | Twig templates, theme engine, modules for layout | Layouts and partials; rendered at build time |
| **Headless CMS** | Content stored/managed separately from presentation | WordPress REST API enables decoupled frontends | JSON:API enables decoupled frontends | Not applicable (presentation is always static files) |
| **Front Matter** | Metadata block at the top of a content file | Not used; metadata in database | Not used; metadata in database | YAML or TOML block (--- or +++) at top of file defining metadata |

---

## Content Model

### WordPress

WordPress stores all content in a single `wp_posts` table, differentiated by the `post_type` column. [Built-in post types include **post** (blog entries), **page** (static pages), and **attachment** (media files).](https://developer.wordpress.org/plugins/post-types/) [Custom post types can be registered by developers.](https://developer.wordpress.org/plugins/post-types/)

**Post Meta**: [Additional data is stored in the `wp_postmeta` table as unstructured key-value pairs, allowing arbitrary metadata attachment without schema changes.](https://developer.wordpress.org/plugins/posts/post-meta/)

**Taxonomies**: [WordPress provides two built-in taxonomies—categories (hierarchical) and tags (flat)—and allows custom taxonomies.](https://developer.wordpress.org/plugins/taxonomies/) Terms are stored in the `wp_terms` and `wp_term_taxonomy` tables.

### Drupal

[Drupal's content model centers on **Entities**: items of content or configuration data.](https://drupal.org/docs/drupal-apis/entity-api) [**Content Entities** (articles, pages, comments) store user-facing content with structured fields.](https://drupal.org/docs/drupal-apis/entity-api)

[**Bundles** (also called content types) are subtypes of entities that share field definitions. For example, a "Recipe" and "Vendor" might both be Node entities but different bundles with different fields.](https://www.drupal.org/docs/user_guide/en/glossary.html) [**Fields** are typed data attached to content entities—text, images, references to other entities, etc.](https://www.drupal.org/docs/user_guide/en/glossary.html)

[**Taxonomy** in Drupal is a classification system using vocabularies (e.g., "Topics") and terms (e.g., "Food," "Agriculture") to organize content.](https://www.drupal.org/docs/user_guide/en/glossary.html)

### Static-Site Generators

Hugo and Jekyll store content as **flat files in the file system**, with front matter metadata at the top of each file. [**Front Matter** in Hugo can be written in YAML, TOML, or JSON and includes reserved fields like `title`, `date`, `draft`, `slug`, `publishDate`, `expiryDate`, and custom parameters.](https://gohugo.io/content-management/front-matter/)

[**Sections** in Hugo are top-level directories or any directory with an `_index.md` file; they organize content hierarchically and determine template selection.](https://gohugo.io/content-management/sections/) [**Taxonomies** in Hugo are user-defined classifications (e.g., tags, genres, actors) assigned in front matter; Hugo automatically generates term pages.](https://gohugo.io/content-management/taxonomies/)

[Jekyll uses a `_posts` folder for blog posts and a `_drafts` folder for unpublished content. Posts require filenames in `YEAR-MONTH-DAY-title.MARKUP` format.](https://jekyllrb.com/docs/posts/) [Front matter in Jekyll is a YAML block at the start of each file with predefined variables like `layout`, `permalink`, `published`, `date`, and custom variables.](https://jekyllrb.com/docs/front-matter/)

---

## Users & Roles

### WordPress

[WordPress defines six **default roles** with hierarchical permission levels:](https://wordpress.org/support/article/roles-and-capabilities/)
- **Super Admin**: Network administration (multisite only)
- **Administrator**: Full site access
- **Editor**: Publish, edit, and moderate posts
- **Author**: Publish and edit own posts
- **Contributor**: Submit posts for review (cannot publish)
- **Subscriber**: Read-only access

[**Capabilities** are fine-grained permissions—e.g., `edit_posts`, `publish_posts`, `upload_files`, `manage_categories`.](https://developer.wordpress.org/plugins/users/roles-and-capabilities/) Roles bundle capabilities; custom roles can be created with any capability set.

### Drupal

[Drupal has two **built-in roles**: Anonymous (unauthenticated visitors) and Authenticated (logged-in users). Site administrators can create additional custom roles.](https://www.drupal.org/docs/user_guide/en/user-roles.html)

[**Permissions** are assigned to roles—e.g., "create node" or "view published content."](https://www.drupal.org/docs/user_guide/en/user-roles.html) Permissions are fine-grained and tied to entity operations and modules.

### Static-Site Generators

SSGs have **no runtime user model**. Access control is delegated to the git repository host (GitHub, GitLab) and the file system. Build and deployment are typically controlled through CI/CD pipelines (GitHub Actions, GitLab CI) with repository-level permissions.

---

## Publishing Workflow

### WordPress

[WordPress uses **post statuses** stored in the `post_status` column of `wp_posts`:](https://wordpress.org/documentation/article/post-status/)
- **publish**: Publicly visible
- **draft**: Incomplete, visible only to users who can edit it
- **pending**: Awaiting review before publication (submitted by Contributors, reviewed by Editors)
- **future**: Scheduled for publication at a future date
- **private**: Visible only to Administrators
- **trash**: Deleted but recoverable
- **auto-draft**: Placeholder post WordPress creates when the editor opens, before anything is saved (autosaves are stored as revisions with status `inherit`)
- **inherit**: For child posts (attachments, revisions); inherits parent status

[Users with only `edit_posts` capability but not `publish_posts` see a "Submit for Review" button instead of "Publish."](https://wordpress.org/documentation/article/post-status/) [**Revisions** are stored as children in the `wp_posts` table with `post_type='revision'` and inherit parent status; autosaves are special revisions that overwrite previous autosaves for each user.](https://wordpress.org/documentation/article/revisions/)

### Drupal

[Drupal's base system has a simple **Published** boolean flag determining if content is visible to the public.](https://www.drupal.org/docs/user_guide/en/content-create.html) [The **Content Moderation** core module (with the core Workflows module) adds workflow states beyond published/unpublished, allowing multi-step approval processes.](https://www.drupal.org/docs/8/core/modules/content-moderation/overview)

[Drupal core supports **revisions** for content entities, allowing content creators to track and restore previous versions.](https://drupal.org/docs/drupal-apis/entity-api)

### Static-Site Generators

[**Jekyll** stores draft posts in a `_drafts` folder without date-based filenames. To publish, a draft is moved to `_posts` and given a date-based filename.](https://jekyllrb.com/docs/posts/) [Building with the `--drafts` flag includes draft posts; the standard build omits them.](https://jekyllrb.com/docs/posts/)

[**Hugo** uses the `draft` field in front matter (draft: true or draft: false).](https://gohugo.io/content-management/front-matter/) The build respects this flag; the `--buildDrafts` flag includes drafts in the output. [Hugo also supports `publishDate` and `expiryDate` for scheduled content.](https://gohugo.io/content-management/front-matter/)

---

## Rendering & Delivery

### WordPress

WordPress is a **dynamic, request-time system**. On each HTTP request, WordPress queries the database, constructs the post/page, runs filters/hooks, and renders HTML using PHP templates. [The **REST API** provides JSON endpoints for all post types, enabling decoupled/headless architectures where content is fetched and rendered by external applications.](https://developer.wordpress.org/rest-api/)

**Themes** use PHP template files (e.g., `single.php`, `page.php`, `archive.php`) with direct database queries and template logic.

### Drupal

Drupal is also **dynamic, request-time system**. On each request, Drupal loads the entity, applies access checks, and renders it using Twig templates and the rendering pipeline. [**JSON:API** is a module that exposes all entity types and bundles via standard REST endpoints, supporting filtering, pagination, and CRUD operations for headless use.](https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/jsonapi)

**Themes** use Twig templates and can override rendering through the theme hook system.

### Static-Site Generators

Hugo and Jekyll are **build-time systems**. During the build phase, all content files are parsed, front matter is extracted, content is rendered through template engines, and the entire site is written to a `site/` or `_site/` directory as static HTML and assets. This output is deployed directly to a web host (e.g., GitHub Pages) with no database or server-side processing.

- **Hugo**: Content → (Front matter + Markdown) → Templates → Static HTML/CSS/JS
- **Jekyll**: Content → (Front matter + Markdown) → Liquid templates → Static HTML/CSS/JS

No REST API or dynamic content delivery; all content is pre-built.

---

## Side-by-Side Comparison

| **Aspect** | **WordPress** | **Drupal** | **Hugo** | **Jekyll** |
|---|---|---|---|---|
| **Primary Data Store** | Database (wp_posts, wp_postmeta, wp_terms) | Database (node, field_*, taxonomy_*) | Flat files (Markdown + YAML/TOML) | Flat files (Markdown + YAML) |
| **Content Units** | Post types (post, page, custom) | Entities with bundles (e.g., Node > Article, Node > Page) | Files in sections | Files in \_posts, pages |
| **Metadata** | Post meta (postmeta table; unstructured) | Fields (typed, defined on bundle) | Front matter (YAML/TOML) | Front matter (YAML) |
| **Taxonomies** | Categories, tags, custom taxonomies | Vocabularies with terms | Custom taxonomies in front matter | Categories, tags in front matter |
| **Default Roles** | 6: Super Admin, Admin, Editor, Author, Contributor, Subscriber | Anonymous, Authenticated, custom | N/A (static output) | N/A (static output) |
| **Permissions Model** | Capabilities (fine-grained; tied to roles) | Permissions (fine-grained; tied to roles) | Git repo permissions (repository access control) | Git repo permissions (repository access control) |
| **Publishing Status** | 8 statuses: publish, draft, pending, future, private, trash, auto-draft, inherit | Published (boolean) + optional workflow states | draft: true/false + publishDate/expiryDate in front matter | File location (_drafts or _posts) + published: false in front matter |
| **Revisions** | Stored as post children (post_type='revision') in database | Revisions table; tracked per entity | Git history (source control) | Git history (source control) |
| **Rendering** | Dynamic per request (PHP) | Dynamic per request (Drupal routing/rendering pipeline) | Build-time (static output) | Build-time (static output) |
| **URL Structure** | Customizable per post type (settings + slug) | Path aliases (configurable per entity) | Directory + filename (slug in front matter optional) | Directory + filename (permalink in front matter optional) |
| **Content Decoupling** | REST API (WordPress REST API) | JSON:API module | Not applicable | Not applicable |
| **Version Control Friendly** | Database exports; site.sql + uploads/ directory | Database exports; site.sql + uploads/ directory | Entire site in Git (files + config) | Entire site in Git (files + config) |

---

## Implications for a Small Local-Admin + Static-Publish CMS

*This section captures inferences and design considerations, not sourced fact. These are observations for your IPHS 400 CMS architecture.*

1. **Content Model**: A minimal content model needs only one primary type (analogous to "post" or "article"). Custom post meta or fields are useful but not essential; simple key-value storage (like WordPress postmeta) is sufficient for drafts and published content.

2. **Roles & Capabilities**: A small admin console needs only two roles: **Admin** (can create, edit, and publish all content) and potentially **Editor** (can edit but not publish). The Subscriber/Contributor distinction (as in WordPress) is overkill for a local admin tool.

3. **Statuses & Drafts**: The minimal useful set is **draft** (editable, not published) and **published** (exported to static site). Additional statuses (pending, future, private, trash) are nice-to-have but not required. Storing drafts in the database and published content as static files is safe and isolates unpublished work.

4. **Publishing Workflow**: Your `cms publish` command mirrors the SSG build process: query published content from the database, render it to HTML, write to `site/`. This is simpler than WordPress's per-request rendering and safer than SSGs requiring filesystem edits.

5. **Revisions**: Tracking old versions of a post is useful but can be deferred. A simple approach: store `created_at` and `updated_at` timestamps; keep the full edit history in the database without a separate revisions table.

6. **Permalinks**: Ensure slug stability early. Once a post is published and included in static site, changing its slug breaks existing links. Store slugs as an explicit field; derive permalink at publish time.

7. **Taxonomies**: Categories or tags can be added later. For MVP, a single content table with no taxonomy is sufficient.

8. **CSRF Protection**: Crucially, every state-changing form must carry a CSRF token (as noted in CLAUDE.md). SQLite + Jinja templates make this straightforward via session-based tokens.

9. **Markdown & Sanitization**: Markdown support for body content is natural; always sanitize it before rendering (use a library like `bleach` or `markupsafe`) to prevent XSS in drafts and published HTML alike.

---

## Sources

- [WordPress Post Status documentation](https://wordpress.org/documentation/article/post-status/)
- [WordPress Revisions documentation](https://wordpress.org/documentation/article/revisions/)
- [WordPress Roles and Capabilities documentation](https://wordpress.org/support/article/roles-and-capabilities/)
- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/)
- [WordPress Plugin: Post Types](https://developer.wordpress.org/plugins/post-types/)
- [WordPress Plugin: Taxonomies](https://developer.wordpress.org/plugins/taxonomies/)
- [WordPress Plugin: Roles and Capabilities](https://developer.wordpress.org/plugins/users/roles-and-capabilities/)
- [Drupal Entity API documentation](https://drupal.org/docs/drupal-apis/entity-api)
- [Drupal Glossary (User Guide)](https://www.drupal.org/docs/user_guide/en/glossary.html)
- [Drupal User Roles documentation](https://www.drupal.org/docs/user_guide/en/user-roles.html)
- [Drupal Content Creation (Published flag)](https://www.drupal.org/docs/user_guide/en/content-create.html)
- [Drupal JSON:API Module documentation](https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/jsonapi)
- [Hugo: Content Organization documentation](https://gohugo.io/content-management/organization/)
- [Hugo: Front Matter documentation](https://gohugo.io/content-management/front-matter/)
- [Hugo: Sections documentation](https://gohugo.io/content-management/sections/)
- [Hugo: Taxonomies documentation](https://gohugo.io/content-management/taxonomies/)
- [Jekyll: Posts documentation](https://jekyllrb.com/docs/posts/)
- [Jekyll: Front Matter documentation](https://jekyllrb.com/docs/front-matter/)
