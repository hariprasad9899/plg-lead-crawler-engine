```
lead-crawler-engine/

├── apps/
│
│   ├── api/
│   │
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── middleware/
│   │   ├── validators/
│   │   ├── plugins/
│   │   ├── app.ts
│   │   └── server.ts
│   │
│   ├── crawler-worker/
│   │
│   │   ├── workers/
│   │   │   └── crawlWorker.ts
│   │   │
│   │   ├── jobs/
│   │   │   └── crawlJob.ts
│   │   │
│   │   └── index.ts
│   │
│   ├── search-worker/
│   │
│   │   ├── jobs/
│   │   │   └── searchJob.ts
│   │   │
│   │   └── index.ts
│   │
│   ├── enrichment-dispatcher/
│   │
│   │   ├── jobs/
│   │   │   └── enrichmentJob.ts
│   │   │
│   │   ├── clients/
│   │   │   └── pythonAiClient.ts
│   │   │
│   │   └── index.ts
│   │
│   └── scheduler/
│
│       ├── cron/
│       │
│       ├── stalePageRecrawl.ts
│       ├── cleanupQueue.ts
│       ├── refreshCompanies.ts
│       │
│       └── index.ts
│
│
├── core/
│
│   ├── ai/
│   │
│   │   ├── prompts/
│   │   │
│   │   ├── intent.prompt.ts
│   │   └── query.prompt.ts
│   │
│   │
│   ├── services/
│   │
│   │   ├── generateIntent.ts
│   │   ├── generateQueries.ts
│   │   └── expandQueries.ts
│   │
│   └── schemas/
│
│       ├── intent.schema.ts
│       └── query.schema.ts
│
│
│
│   ├── crawler/
│   │
│   │   ├── crawlPage.ts
│   │   ├── normalizeUrl.ts
│   │   ├── extractLinks.ts
│   │   ├── enqueueChildren.ts
│   │   ├── scoreUrl.ts
│   │   └── robotsChecker.ts
│
│
│   ├── extraction/
│   │
│   │   ├── extractEmails.ts
│   │   ├── extractPhones.ts
│   │   ├── extractSocials.ts
│   │   ├── extractMetadata.ts
│   │   ├── detectTechnology.ts
│   │   ├── detectHiring.ts
│   │   └── aggregateSignals.ts
│
│
│   ├── search/
│   │
│   │   ├── providers/
│   │   │
│   │   ├── serper.provider.ts
│   │   ├── brave.provider.ts
│   │   └── tavily.provider.ts
│   │
│   └── discoverSeedUrls.ts
│
│
│   ├── queue/
│   │
│   │   ├── bullmq.ts
│   │   ├── producers.ts
│   │   ├── consumers.ts
│   │   └── queues.ts
│
│
│   ├── database/
│   │
│   │   ├── repositories/
│   │   │
│   │   ├── companyRepo.ts
│   │   ├── crawlRepo.ts
│   │   ├── contactRepo.ts
│   │   ├── seedRepo.ts
│   │   └── jobRepo.ts
│   │
│   └── prismaClient.ts
│
│
│   ├── logger/
│   │
│   │   ├── logger.ts
│   │   └── requestLogger.ts
│
│
│   ├── config/
│   │
│   │   ├── env.ts
│   │   └── constants.ts
│
│
│   ├── types/
│   │
│   │   ├── company.ts
│   │   ├── crawl.ts
│   │   ├── signals.ts
│   │   └── search.ts
│
│
│   └── utils/
│
│       ├── retry.ts
│       ├── sleep.ts
│       ├── hash.ts
│       ├── sanitize.ts
│       └── dedupe.ts
│
│
├── prisma/
│
│   ├── schema.prisma
│   └── migrations/
│
│
├── scripts/
│
│   ├── migrate.ts
│   ├── seed.ts
│   └── cleanup.ts
│
│
├── tests/
│
│   ├── crawler/
│   ├── extraction/
│   └── search/
│
│
├── docs/
│
│   ├── architecture.md
│   ├── db-design.md
│   ├── queue-flow.md
│   └── ai-flow.md
│
│
├── docker/
│
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   └── Dockerfile.scheduler
│
│
├── .env
├── docker-compose.yml
├── package.json
├── tsconfig.json
├── pnpm-workspace.yaml
├── README.md
└── turbo.json
```
