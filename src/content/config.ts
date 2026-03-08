import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.enum(['Dispatches', 'Field Notes', 'The Machine', 'Case Files', 'Persona']))
  })
});

export const collections = { blog };
