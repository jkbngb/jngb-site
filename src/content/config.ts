import { defineCollection, z } from 'astro:content';

const notes = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    heading: z.string().optional(),
    summary: z.string(),
    date: z.string(),
    tags: z.array(z.string()).optional(),
    stack: z.array(z.string()).optional(),
  }),
});

export const collections = { notes };
