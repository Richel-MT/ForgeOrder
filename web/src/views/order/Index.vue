<template>
    <div>
        <TopBar :showHome="true">
        <template #left>
            <mdui-button-icon @click="goBack">
                <mdui-icon-arrow-back></mdui-icon-arrow-back>
            </mdui-button-icon>
        </template>
        </TopBar>


        <router-view/>
    </div>

</template> 


<script setup>
    import TopBar from '@/components/TopBar.vue'

    import { goBack } from '@/utils/routerHelper.js'

    import { onMounted } from 'vue'
    import { useRoute } from 'vue-router'

    const route = useRoute()

    onMounted(() => {
        if (route.path == '/order') {
            goBack()
        }
    })

</script>