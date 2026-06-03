import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
})

export const PLANS = {
  free: {
    name: 'Free',
    priceId: null,
    limits: {
      documents: 5,
      wordsPerDoc: 2000,
    },
  },
  pro: {
    name: 'Pro',
    priceId: 'price_pro_monthly', // Replace with your Stripe price ID
    limits: {
      documents: 100,
      wordsPerDoc: 10000,
    },
  },
  enterprise: {
    name: 'Enterprise',
    priceId: 'price_enterprise_monthly', // Replace with your Stripe price ID
    limits: {
      documents: 'unlimited',
      wordsPerDoc: 50000,
    },
  },
} as const
