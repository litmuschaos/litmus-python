//import java.text.SimpleDateFormat

def l1 = 'dev'
def l2 = 'tools'
def serviceName = 'litmus-python'
def region = 'usw2'
def iksType = 'ppd'
def appName = "${l1}-${l2}-${serviceName}-${region}-${iksType}"
def deployable_branches = ["master"]
// def argocd_server = new URL("https://cdp.argocd.tools-k8s-prd.a.intuit.com").getHost() + ":443"
// def argocd_password = "argocd-${serviceName}"
// def kson_compnt= "sample"
def ptNameVersion = "${serviceName}-${UUID.randomUUID().toString().toLowerCase()}"
def repo = "dev/tools/litmus-python/service"
def deploy_repo = "github.intuit.com/dev-tools/litmus-python.git"
def tag = ""
def registry = "docker.artifactory.a.intuit.com"
def image = "${repo}/${serviceName}"
def app_wait_timeout = 3600
// def prd_diff_msg = ""
// def stage_timeout = 20
def git_timeout = 2
def preprodOnly = true


podTemplate(name: ptNameVersion, label: ptNameVersion, containers: [
   // containerTemplate(name: 'python', image: 'python:3.6-jessie', ttyEnabled: true, command: 'cat', args: '' ),
    containerTemplate(name: 'docker', image: 'docker.artifactory.a.intuit.com/dev/build/ibp/jnlp-slave-with-docker:18.03.0', ttyEnabled: true, command: 'cat', args: '')
    ],
    volumes: [hostPathVolume(hostPath: '/var/run/dind/docker.sock', mountPath: '/var/run/docker.sock')]
  )

{
    // DO NOT CHANGE
    def isPR = env.CHANGE_ID != null
    def branch = env.CHANGE_ID != null ? env.CHANGE_TARGET : env.BRANCH_NAME

    // exit gracefully if not the master branch (or, rather, not in deployable_branches)
    if (!deployable_branches.contains(branch)) {
        stage("Skipping pipeline") {
            println "Branch: ${branch} is not part of deployable_branches"
            println "Skipping pipeline"
        }
        currentBuild.result = 'SUCCESS'
        return
    }

    node(ptNameVersion) {
        // DO NOT CHANGE
        def scmInfo = checkout scm
        def shortCommit = "${scmInfo.GIT_COMMIT}"[0..6]
        tag = "${env.BUILD_TAG}-${shortCommit}"
        def hasReleaseTag = sh(returnStdout: true, script: 'git tag --points-at HEAD').trim().startsWith('release-')

        // Build Stage
        stage('Build') {
            withCredentials([usernamePassword(credentialsId: "artifactory-${serviceName}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
//                 container('python') {
//                     sh "echo Test 1"
//                     sh "cp pip.conf /etc/pip.conf"
//                     sh "mkdir packages"
//                     sh "pip download -r requirements.txt -d packages"
//                 }
                container('docker') {
                    sh "echo ${DOCKER_PASSWORD} | docker login ${registry} -u ${DOCKER_USERNAME} --password-stdin"
                    if(isPR){
						sh "cd chaostoolkit/ && DOCKER_BUILDKIT=1 docker build -f Dockerfile . -t ${registry}/${image}:${tag}"
						sh "docker push ${registry}/${image}:${tag}"
                    } else {
						sh "cd chaostoolkit/ && DOCKER_BUILDKIT=1 docker build -f Dockerfile . -t ${registry}/${image}:${tag}"
						sh "docker push ${registry}/${image}:${tag}"
                    }
                   sh "docker logout ${registry}"
                }
            }
        }
}


