import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import StatePanel from '@/components/StatePanel.vue'

describe('StatePanel', () => {
  it('renders title and message', () => {
    const wrapper = mount(StatePanel, {
      props: { variant: 'empty', title: 'No data', message: 'Add your first record.' },
      global: {
        stubs: {
          ProgressSpinner: true,
        },
      },
    })

    expect(wrapper.text()).toContain('No data')
    expect(wrapper.text()).toContain('Add your first record.')
  })
})

