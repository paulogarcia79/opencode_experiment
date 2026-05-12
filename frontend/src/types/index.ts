import type { JSONContent } from '@tiptap/vue-3'

export interface Tag {
  id: string
  name: string
  slug: string
  article_count?: number
  created_at?: string
}

export interface ArticleAuthor {
  id: string
  email: string
}

export interface Article {
  id: string
  title: string
  slug: string
  content: JSONContent
  description: string | null
  status: string
  send_newsletter: boolean
  published_at: string | null
  scheduled_for: string | null
  search_text: string | null
  created_at: string
  updated_at: string
  author: ArticleAuthor | null
  tags: Tag[]
}

export interface ArticlePerformance {
  id: string
  title: string
  slug: string
  status: string
  published_at: string | null
  total_views: number
  unique_views_24h: number
  email_sent: number
  email_opens: number
  email_clicks: number
  email_open_rate: number
  email_ctr: number
}

export interface ArticleWithPerformance extends Article {
  total_views?: number
  unique_views_24h?: number
  email_sent?: number
  email_opens?: number
  email_clicks?: number
  email_open_rate?: number
  email_ctr?: number
}

export interface AnalyticsSummary {
  total_active: number
  total_pending: number
  total_unsubscribed: number
  total_opens: number
  total_clicks: number
  total_bounces: number
  total_complaints: number
  open_rate: number
  ctr: number
  bounce_rate: number
  complaint_rate: number
}

export interface GrowthSeries {
  date: string
  count: number
}

export interface AnalyticsGrowth {
  signups: GrowthSeries[]
  unsubscribes: GrowthSeries[]
  opens: GrowthSeries[]
  clicks: GrowthSeries[]
  bounces: GrowthSeries[]
  complaints: GrowthSeries[]
}

export interface AnalyticsDelivery {
  sent: number
  failed: number
  pending: number
}

export interface AnalyticsData {
  summary: AnalyticsSummary
  growth: AnalyticsGrowth
  delivery: AnalyticsDelivery
}

export interface SearchResult {
  id: string
  title: string
  slug: string
  description: string | null
  published_at: string
}

export interface TagSuggestion {
  name: string
  slug: string
  article_count?: number
}

export interface TagArticlesResponse {
  name: string
  slug: string
  articles: Article[]
}

export interface ImportSuccess {
  id: string
  title: string
  slug: string
}

export interface ImportError {
  filename: string
  error: string
}

export interface ImportResult {
  successes: ImportSuccess[]
  errors: ImportError[]
  total: number
}

export interface ImageAsset {
  id: string
  url: string
  original_name: string
  size_bytes: number
  mime_type: string
  created_at: string
}

export interface ConnectedAccount {
  email: string
  is_verified: boolean
  connected_providers: { provider: string; connected_at: string }[]
}

export type TipTapContent = JSONContent

export interface RevisionListItem {
  version_number: number
  change_type: string
  title: string
  created_at: string
  author_email: string | null
}

export interface Revision {
  version_number: number
  change_type: string
  title: string
  content: Record<string, unknown>
  description: string | null
  tag_names: string[]
  created_at: string
  author_email: string | null
}
