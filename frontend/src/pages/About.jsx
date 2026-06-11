import React from 'react'
import { BrainCircuit, Database, FileCode2, Gauge, ShieldCheck, Sparkles } from 'lucide-react'

const capabilities = [
  {
    icon: BrainCircuit,
    title: 'Vision-first recognition',
    text: 'Transforms handwritten math images into structured LaTeX with model confidence and symbol metadata.',
  },
  {
    icon: FileCode2,
    title: 'Production outputs',
    text: 'Copy, download, render, and reuse expressions across reports, notebooks, docs, and learning tools.',
  },
  {
    icon: Database,
    title: 'History workspace',
    text: 'Search prior predictions, inspect rendered equations, and clean up records from one focused view.',
  },
]

const stats = [
  ['YOLOv11', 'Recognition engine'],
  ['LaTeX', 'Export format'],
  ['FastAPI', 'Backend service'],
  ['React', 'Interface layer'],
]

export default function About() {
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm dark:border-white/10 dark:bg-neutral-900">
        <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="inline-flex items-center gap-2 rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700 dark:border-sky-400/20 dark:bg-sky-400/10 dark:text-sky-300">
              <Sparkles className="h-3.5 w-3.5" />
              AI math recognition workspace
            </div>
            <h1 className="mt-5 max-w-3xl text-3xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-4xl">
              Handwritten Maths Formula turns rough equation images into clean, usable LaTeX.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-600 dark:text-neutral-400">
              The product combines upload workflows, rendering, export actions, and saved prediction history into a compact interface for students, researchers, and technical teams.
            </p>
          </div>
          <div className="border-t border-slate-200 bg-slate-950 p-6 text-white dark:border-white/10 lg:border-l lg:border-t-0">
            <div className="grid h-full content-between gap-6">
              <div className="rounded-lg border border-white/10 bg-white/5 p-5">
                <Gauge className="h-6 w-6 text-emerald-300" />
                <p className="mt-4 text-sm text-neutral-300">Designed for fast review loops after every model prediction.</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {stats.map(([value, label]) => (
                  <div key={label} className="rounded-lg border border-white/10 bg-white/5 p-4">
                    <p className="text-sm font-semibold">{value}</p>
                    <p className="mt-1 text-xs text-neutral-400">{label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {capabilities.map((item) => {
          const Icon = item.icon
          return (
            <article key={item.title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-neutral-900">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700 dark:bg-white/10 dark:text-white">
                <Icon className="h-5 w-5" />
              </div>
              <h2 className="mt-4 text-base font-semibold text-slate-950 dark:text-white">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-neutral-400">{item.text}</p>
            </article>
          )
        })}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-neutral-900">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Operational Principles</h2>
            <p className="mt-1 text-sm text-slate-600 dark:text-neutral-400">Fast feedback, transparent confidence, editable output, and durable history.</p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700 dark:border-emerald-400/20 dark:bg-emerald-400/10 dark:text-emerald-300">
            <ShieldCheck className="h-4 w-4" />
            Ready for iterative workflows
          </div>
        </div>
      </section>
    </div>
  )
}
