# Medium engagement queue

The queue is a review surface, not a posting bot. A signed-in, user-initiated research session may add up to five candidates after reading the source stories. Every candidate must include the exact Medium URL, author, title, a concrete reason for engagement, evidence from the story, and a specific draft response.

Allowed candidate states are `proposed`, `ready_for_confirmation`, `posted`, and `skipped`. Moving a candidate to `ready_for_confirmation` does not authorize a Medium action. Immediately before posting, the operator must show the exact target and response text and obtain confirmation. After posting, the public response URL is verified and a `response_posted` receipt is recorded.

GitHub Actions validates the queue, creates review artifacts, and resumes reporting after a receipt is committed. It never signs in to Medium, posts a response, claps, highlights, follows, reposts, or creates traffic.
