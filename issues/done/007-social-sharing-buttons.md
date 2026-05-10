# [Slice 7] Social Sharing Buttons

**GitHub Issue:** #007
**Labels:** needs-triage
**State:** open

## Parent

PRD: Social Sharing Buttons (`PRD-social-sharing-buttons.md`)

## What to build

Add icon-only social sharing buttons to the article detail page, positioned between the article body and the newsletter subscription form. Buttons for Twitter/X, LinkedIn, and Copy Link. Twitter/X and LinkedIn open in a new tab with UTM parameters. Copy Link copies a clean URL to clipboard and shows a toast notification.

## Acceptance criteria

- [ ] New `ShareButtons` Vue component with props: `url`, `title`, `description`
- [ ] Component renders three icon-only buttons: Twitter/X, LinkedIn, Copy Link
- [ ] Twitter/X button opens `https://twitter.com/intent/tweet?url=...&text=...` with UTM params in new tab
- [ ] LinkedIn button opens `https://www.linkedin.com/sharing/share-offsite/?url=...` with UTM params in new tab
- [ ] Copy Link button copies clean article URL (no UTM) to clipboard
- [ ] Copy success shows "Link copied to clipboard" toast notification
- [ ] Buttons have subtle background hover effect consistent with existing design system
- [ ] Each button has `aria-label` for accessibility
- [ ] ShareButtons component rendered on article detail page between article body and newsletter form
- [ ] Share buttons only appear when article has loaded successfully (not during loading/error states)
- [ ] Component tested: renders buttons, correct URLs, UTM params, copy behavior, toast notification

## Blocked by

None - can start immediately
