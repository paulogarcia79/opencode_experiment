## Problem Statement

Readers who enjoy published articles have no way to share them on social platforms. There are no Twitter/X, LinkedIn, or copy-link buttons on the article detail page. This limits organic reach, reduces referral traffic, and makes the platform feel less like a modern publishing tool. The article page ends with a newsletter subscription form but offers no mechanism for readers to spread content they find valuable.

## Solution

Add a set of icon-only social sharing buttons to the article detail page, positioned between the article body and the newsletter subscription form. The buttons allow readers to share the current article on Twitter/X, LinkedIn, or copy a clean link to their clipboard. Each button opens in a new tab (where applicable), uses subtle hover feedback consistent with the dark tech design system, and shows a toast notification on successful link copy.

## User Stories

1. As a reader who enjoyed an article, I want to share it on Twitter/X with a single click, so that I can spread valuable content to my followers
2. As a reader who found an article professionally relevant, I want to share it on LinkedIn, so that my network can discover the content
3. As a reader who wants to share an article in a private channel (Slack, email, DM), I want to copy the article URL to my clipboard, so that I can paste it anywhere
4. As a site owner, I want shared Twitter/X and LinkedIn links to include UTM parameters, so that I can track which social platforms drive traffic in analytics
5. As a site owner, I want the copy-link action to provide a clean URL without UTM parameters, so that pasted links look natural in private channels
6. As a reader on mobile, I want share buttons to open Twitter/LinkedIn in a new tab, so that I do not lose my place on the article page
7. As a reader, I want visual feedback (tooltip on hover, toast on copy) when interacting with share buttons, so that I know the system responded to my action
8. As a developer, I want the share buttons implemented as a reusable component, so that they can be added to other pages (e.g., homepage cards) without duplication
9. As a developer, I want the component to accept `url`, `title`, and `description` as props, so that it is decoupled from the article page's data fetching logic
10. As a reader, I want the share buttons to match the dark tech aesthetic of the site, so that they feel native and not like third-party widgets
11. As a site owner, I want the share buttons to only appear on published article pages, so that draft or error pages never expose sharing actions
12. As a reader with a slow connection, I want share buttons to render instantly without external JavaScript SDKs, so that the page remains fast and lightweight

## Implementation Decisions

### Modules

**ShareButtons Vue Component**
- A new reusable component with props: `url`, `title`, `description`
- Encapsulates all share-link generation logic (UTM appending, platform-specific URL formats)
- Renders three icon-only buttons in a horizontal row with consistent spacing
- Handles hover states, click events, clipboard copy, and toast notification dispatch
- Uses SVG icons inline (no external icon libraries, consistent with existing design system)
- Deep module: simple props interface, hides all platform URL construction and interaction logic internally

**Article Page Integration**
- The article detail page imports the ShareButtons component and renders it between the article body and the newsletter subscription form
- Passes the current article's URL, title, and description as props
- Only renders when the article has loaded successfully (not during loading or error states)

### Share URL Construction

- **Twitter/X**: `https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}`
- **LinkedIn**: `https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}`
- **Copy link**: Raw article URL with no query parameters

- UTM parameters appended to Twitter/X and LinkedIn URLs only:
  - `?utm_source=share&utm_medium=twitter&utm_campaign=social`
  - `?utm_source=share&utm_medium=linkedin&utm_campaign=social`
- Copy link remains clean (no UTM) for natural pasting in private channels

### Visual Design

- Icon-only buttons (no text labels)
- SVG icons for each platform (Twitter bird, LinkedIn "in", link/copy icon)
- Horizontal flex layout with consistent gap spacing
- Hover: subtle background lightening (`bg-white/5` → `bg-white/10`), consistent with existing button patterns
- Tooltips on hover showing platform name (e.g., "Share on X", "Share on LinkedIn", "Copy link")
- No platform brand colors — uses the site's slate/white palette to maintain dark tech aesthetic

### Interaction Behavior

- Twitter/X and LinkedIn: open in new tab (`target="_blank" rel="noopener noreferrer"`)
- Copy link: uses `navigator.clipboard.writeText()`, falls back to legacy `document.execCommand('copy')`
- Toast notification on successful copy: "Link copied to clipboard" (reuses existing toast pattern from AdminMediaView)
- No toast for Twitter/LinkedIn clicks (new tab opening is self-evident feedback)

### No Backend Changes

- This is a pure frontend feature
- No new API endpoints, no database schema changes, no server-side logic
- Share URLs are constructed client-side from the current page URL and article metadata

## Testing Decisions

**What makes a good test:** Test external behavior only — rendered buttons, generated href attributes, click behavior, and toast visibility. Do not test internal URL construction helpers as separate units; test them through the component's rendered output.

**Modules to test:**
- `ShareButtons` component: verify three buttons render with correct icons, verify Twitter link contains UTM params and article URL, verify LinkedIn link contains UTM params and article URL, verify copy link is clean (no UTM), verify copy click triggers clipboard write, verify toast appears on copy success, verify hover classes are present

**Prior art:**
- `AdminMediaView.spec.ts` tests toast notifications and button clicks using `@vue/test-utils` and `flushPromises`
- `useImageUpload.spec.ts` mocks global `fetch` and tests async behavior
- `useHead.spec.ts` tests DOM manipulation in a test environment

## Out of Scope

- Homepage article card share buttons (deferred — component is reusable but placement is out of scope)
- Facebook, Reddit, Bluesky, Hacker News, or other platforms (easy to add later without schema changes)
- Web Share API / native OS share sheet (deferred to mobile-specific enhancement)
- Share count display or analytics (purely frontend, no backend counter)
- OG image generation for social previews (already handled by existing OpenGraph meta tags)
- Email share (`mailto:`) — can be added later as a fourth button
- Print button or "read later" integrations

## Further Notes

- The component should accept a `baseUrl` prop or derive it from `window.location` to ensure it works correctly behind Nginx proxy in both dev and prod environments
- Tooltip implementation can use native `title` attribute for simplicity, or a custom tooltip component if the design system demands richer styling
- The copy-to-clipboard fallback (`document.execCommand`) is needed for older browsers and iframe contexts where `navigator.clipboard` may be unavailable
- Consider adding `aria-label` attributes to each button for screen reader accessibility
