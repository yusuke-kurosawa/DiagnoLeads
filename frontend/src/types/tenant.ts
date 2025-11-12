export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}
