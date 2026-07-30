<template>
    <div>
        <Transition :name="transitionName" mode="out-in">
            <component :is="currentComponent" :key="index" />
        </Transition>
        
        
        <Transition name="fade">
            <BottomBar 
            ref="bottomBar" 
            v-show="showBottomBar_" 
            />
        </Transition>



    </div>
</template>

<script setup>
    import '@/assets/transition.css'

    import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick, defineAsyncComponent } from 'vue'
    import { useRoute,  useRouter } from 'vue-router'

    import BottomBar from '@/components/BottomBar.vue'

    const Home = defineAsyncComponent(() => import('./Home.vue'))
    const Orders = defineAsyncComponent(() => import('./Orders.vue'))
    const Me = defineAsyncComponent(() => import('./Me.vue'))



    const route = useRoute()
    const router = useRouter()

    const transitionName = ref('tabslide-left')
    const bottomBar = ref(null)

    const lastIndex = ref(0)
    const isInitialized = ref(false)

    // 使用动态组件
    const currentComponent = computed(() => {
        const index = bottomBar.value?.index ?? 0
        const components = [Home, Orders, Me]
        return components[index] || Home
    })

    const index = computed(() => {
        return bottomBar.value?.index ?? 0
    })


    let showTimer = null

    onMounted(async () => {
        await nextTick()

        const queryIndex = route.query?.index
        if (queryIndex) {
            bottomBar.value?.updateIndex(Number(queryIndex))
        } else {
            bottomBar.value?.updateIndex(0)
        }
        bottomBar.value?.setSelected(index.value.toString() || '0')

        isInitialized.value = true

        // 首屏加载：等页面动画结束后再显示 BottomBar，避免 fixed 元素瞬移/闪现
        showTimer = setTimeout(() => {
            showBottomBar_.value = true
        }, 180)
    })

    onBeforeUnmount(() => {
        if (showTimer) clearTimeout(showTimer)
    })

    // 监听 index 变化同步到 URL
    watch(
    () => bottomBar.value?.index ?? -1,
    (newVal, oldVal) => {



        if (!isInitialized.value) {
            return
        }
        
        router.replace({
            query: {
                ...router.currentRoute.value.query,
                index: newVal
            }
        })
        transitionName.value = newVal > lastIndex.value ? 'tabslide-left' : 'tabslide-right'
        lastIndex.value = newVal

    }
)

    // 默认隐藏，等页面动画结束后再显示，避免 fixed 定位的 BottomBar 瞬移/闪现
    const showBottomBar_ = ref(false)

    // 监听路由 path 变化：tab 切换只改 query 不改 path，跨页面切换才改 path
    watch(
        () => route.path,
        (newPath, oldPath) => {
            if (showTimer) clearTimeout(showTimer)

            if (newPath === '/') {
                // 从其他页面进入主页：先隐藏 BottomBar，等页面滑入动画（150ms）结束后再显示
                // 这样 fixed 定位的 BottomBar 不会比页面先出现，造成"瞬移"感
                showBottomBar_.value = false
                showTimer = setTimeout(() => {
                    showBottomBar_.value = true
                }, 180)
            } else if (oldPath === '/') {
                // 离开主页去其他页面：立即隐藏 BottomBar
                // 否则页面滑走时 fixed 的 BottomBar 会"粘"在屏幕底部不跟着走
                showBottomBar_.value = false
            }
        },
        { flush: 'post' }
    )

</script>