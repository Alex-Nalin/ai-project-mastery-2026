import Anthropic from '@anthropic-ai/sdk'
import { createClient } from '@/lib/supabase-server'
import { NextResponse } from 'next/server'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

export async function POST(request: Request) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()
    
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { documentId, content } = await request.json()

    if (!content || content.length > 50000) {
      return NextResponse.json(
        { error: 'Content must be between 1 and 50,000 characters' },
        { status: 400 }
      )
    }

    // Check user's plan limits
    const { data: profile } = await supabase
      .from('profiles')
      .select('subscription_tier')
      .eq('id', user.id)
      .single()

    const tier = profile?.subscription_tier || 'free'
    const limits = {
      free: { maxWords: 2000 },
      pro: { maxWords: 10000 },
      enterprise: { maxWords: 50000 },
    }[tier] || { maxWords: 2000 }

    if (content.split(/\s+/).length > limits.maxWords) {
      return NextResponse.json(
        { error: `Your plan limits summaries to ${limits.maxWords} words` },
        { status: 403 }
      )
    }

    // Generate summary using Claude Opus 4.8
    const response = await anthropic.messages.create({
      model: 'claude-mythos-5-20260401',
      max_tokens: 1024,
      system: `You are an expert executive summarizer. 
      Generate a concise, well-structured summary of the provided text.
      Include:
      - Key points (3-5 bullet points)
      - Main argument or thesis
      - Important data or statistics mentioned
      - Action items or conclusions
      
      Format your response in markdown.`,
      messages: [
        {
          role: 'user',
          content: `Please summarize the following text:\n\n${content}`,
        },
      ],
    })

    const summary = response.content[0].text

    // Save to database
    const { error: updateError } = await supabase
      .from('documents')
      .update({
        summary,
        status: 'completed',
        updated_at: new Date().toISOString(),
      })
      .eq('id', documentId)
      .eq('user_id', user.id)

    if (updateError) {
      console.error('Database update error:', updateError)
    }

    // Log usage
    await supabase.from('usage_logs').insert({
      user_id: user.id,
      action: 'summarize',
      tokens_used: response.usage.input_tokens + response.usage.output_tokens,
    })

    return NextResponse.json({ summary })
  } catch (error) {
    console.error('Summarization error:', error)
    return NextResponse.json(
      { error: 'Failed to generate summary' },
      { status: 500 }
    )
  }
}
