import { Routes } from '@angular/router';
import { ViewHome } from './components/views/view-home/view-home';
import { ViewConfig } from './components/views/view-config/view-config';
import { ViewBase }   from './components/views/view-base/view-base';

import { PipelineView } from './components/views/pipeline-view/pipeline-view';
import { DictionaryView } from './components/views/dictionary-view/dictionary-view';
import { DuplicatesView } from './components/views/duplicates-view/duplicates-view';

import { FzlbpmsContainersView } from './components/views/fzlbpms-containers-view/fzlbpms-containers-view';
import { DesktopHomeView } from './components/views/desktop-home-view/desktop-home-view'
import { MoodleInstallView } from './components/views/moodle-install-view/moodle-install-view';


export const routes: Routes = [

    {
        path:'',
        component: ViewHome
    },

    {
        path:'baseview',
        component: ViewBase
    },
    {
        path:'configs',
        component: ViewConfig
    },
    {
        path:'pipelineview',
        component: PipelineView
    },
    {
        path:'dictionaryview',
        component: DictionaryView
    },
    {
        path:'duplicatesview',
        component: DuplicatesView
    },
    {
        path: 'moodle-install',
        component: MoodleInstallView
    },
    {
        path:'desktophomeview',
        component: DesktopHomeView

    },
    {
        path:'fzlbpms-containers-vew',
        component: FzlbpmsContainersView
    }
];
