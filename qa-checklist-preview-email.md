# QA Checklist: Preview Email Feature

## Prerequisites & Setup
- [ ] Backend server running on port 8000.
- [ ] Frontend server running on port 5173.
- [ ] Database running with at least one saved article (draft or published).
- [ ] `RESEND_API_KEY` configured in `.env` (optional, if missing it just simulates sending).
- [ ] Admin user logged in.

## Backend API Checks
- [ ] **Action:** Send `POST /api/admin/articles/<valid_article_id>/preview-email` with valid Bearer token → **Expected:** `200 OK` with JSON `{"message": "Preview sent successfully"}`
- [ ] **Action:** Send `POST /api/admin/articles/<valid_article_id>/preview-email` without token → **Expected:** `403 Forbidden`
- [ ] **Action:** Send `POST /api/admin/articles/<invalid_id>/preview-email` with valid Bearer token → **Expected:** `404 Not Found` with detail "Article not found"

## Frontend UI Checks
- [ ] **Action:** Navigate to Admin Dashboard and click "New Article" → **Expected:** The "Send Preview" button is NOT visible.
- [ ] **Action:** Type a title to trigger auto-save, wait for "Saved" → **Expected:** The "Send Preview" button appears.
- [ ] **Action:** Open an existing article to edit → **Expected:** The "Send Preview" button is visible.
- [ ] **Action:** Click "Send Preview" → **Expected:** Button text changes to "Sending...", spinner appears, and button is disabled.
- [ ] **Action:** Wait for preview to complete → **Expected:** Button resets, and a green success banner appears saying "Preview sent successfully."

## Edge Cases & Error Handling
- [ ] **Action:** Click "Send Preview" when backend is unreachable or offline → **Expected:** Red error banner appears saying "Failed to send preview." or "Network error".
- [ ] **Action:** Click "Send Preview" on an article that was just deleted in another tab → **Expected:** Red error banner appears saying "Article not found".
- [ ] **Action:** Spam click the "Send Preview" button before the first request completes → **Expected:** Only one request is sent because the button is disabled while `previewing` is true.

## Integration Checks
- [ ] **Action:** Write content with bold text, a link, and an image in the editor, wait for save, click "Send Preview" → **Expected:** Check the `ADMIN_EMAIL` inbox; an email arrives.
- [ ] **Action:** Open the received email → **Expected:** The email content visually matches the TipTap editor (bolding, lists, links), images render with absolute URLs, and a dummy unsubscribe link appears at the bottom.