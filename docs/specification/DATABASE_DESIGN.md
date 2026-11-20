# Database Design — Proposed Later-Phase Schema

## 1. MVP decision

A database is **not required** for the first scan-only MVP. The app can send an image to the API and display the result without storing scan history.

Add Supabase/Postgres only when the product owner approves a feature requiring persistence, such as user accounts, cloud history or feedback. Do not introduce auth/database complexity before the core scan flow works.

## 2. Proposed provider

Supabase (managed PostgreSQL + Auth + Row Level Security) is the proposed option for a later phase. This is a proposal, not an existing dependency.

## 3. Data minimization

Default policy:
- Do not store raw images.
- Do not store image bytes in Postgres.
- Store scan metadata only if the user enables history.
- Avoid collecting precise location unless a location-specific feature is approved and the user grants permission.
- Provide a way to delete user history if cloud history is introduced.

## 4. Proposed entities

### `profiles`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key; references auth user |
| `display_name` | text nullable | Optional |
| `created_at` | timestamptz | Server-generated |

Do not duplicate unnecessary personal information from the auth provider.

### `scans`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Owner; references auth user |
| `created_at` | timestamptz | Server-generated |
| `image_width` | integer | Dimensions only |
| `image_height` | integer | Dimensions only |
| `total_objects` | integer | Non-negative |
| `model_version` | text | Model identifier |
| `client_source` | text nullable | camera/gallery if useful |

No raw image or public image URL by default.

### `scan_detections`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `scan_id` | UUID | References scans |
| `category` | text | Constrained to four canonical classes |
| `confidence` | real | Between 0 and 1 |
| `x1` | real | Original-image coordinate |
| `y1` | real | Original-image coordinate |
| `x2` | real | Original-image coordinate |
| `y2` | real | Original-image coordinate |

### `detection_feedback` (optional)
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Owner |
| `scan_detection_id` | UUID nullable | Reference to detection if retained |
| `reported_category` | text | User's suggested correction |
| `comment` | text nullable | Optional, length-limited |
| `created_at` | timestamptz | Server-generated |

Feedback must not automatically enter training data. It needs review, consent and data-governance controls.

## 5. Relationships

- One auth user has one profile.
- One user has many scans.
- One scan has many detections.
- A feedback record belongs to a user and may refer to a detection.

## 6. Security and RLS

If Supabase is implemented:
- Enable RLS on every user-owned table.
- Users can select/insert/delete only their own records as required.
- Do not expose service-role keys to the mobile app.
- Use the anon/publishable key only with correct RLS policies.
- Restrict update permissions to the minimum needed.
- Test policies with two separate users to verify isolation.
- Use SQL migrations committed to the repository.
- Avoid trusting client-supplied `user_id`; derive identity from authenticated context.

## 7. Indexes and constraints

- Index `scans(user_id, created_at DESC)`.
- Index `scan_detections(scan_id)`.
- Add category check constraint.
- Add `confidence BETWEEN 0 AND 1`.
- Add non-negative counts and positive image dimensions.
- Validate box coordinates against stored image dimensions at application level or with an appropriate database constraint.

## 8. Retention and deletion

Before cloud history ships, define:
- Whether history is opt-in or opt-out.
- Retention period.
- User-visible deletion flow.
- Account deletion behavior.
- Backup retention limitations.
- Whether anonymized aggregates are retained.

## 9. Migrations

Use versioned SQL migrations. Never rely on undocumented manual dashboard edits for production schema. Include a seed only for non-sensitive static category metadata if useful.
